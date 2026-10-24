"""Windows media and audio integration; imports happen in service threads."""
import asyncio
import datetime as dt
import queue
import sys
import threading
import time

from events import emit


def seek_position(timeline,fraction):
    import math
    value=float(fraction)
    if not math.isfinite(value) or not 0<=value<=1:raise ValueError('Invalid playback position')
    duration=(timeline.end_time-timeline.start_time).total_seconds()
    if duration<=0:raise ValueError('Track duration unavailable')
    return round((timeline.start_time.total_seconds()+duration*value)*10_000_000)


async def media_transport(command):
    from winsdk.windows.media.control import GlobalSystemMediaTransportControlsSessionManager as Manager
    manager = await Manager.request_async()
    session = manager.get_current_session()
    if session is None:
        return False
    methods = {'next': 'try_skip_next_async', 'prev': 'try_skip_previous_async',
               'pause': 'try_pause_async', 'resume': 'try_play_async', 'toggle': 'try_toggle_play_pause_async'}
    if command == 'restart':
        return await session.try_change_playback_position_async(0)
    if command.startswith('seek:'):
        return await session.try_change_playback_position_async(seek_position(session.get_timeline_properties(),command.split(':',1)[1]))
    return await getattr(session, methods[command])()


def transport(command):
    return asyncio.run(media_transport(command))


class MediaService:
    def __init__(self):
        self.stopped = threading.Event()
        self.thread = None
        self.snapshot = {}

    def start(self):
        self.thread = threading.Thread(target=lambda: asyncio.run(self._run()), name='Kai media', daemon=True)
        self.thread.start()

    async def _run(self):
        try:
            from winsdk.windows.media.control import GlobalSystemMediaTransportControlsSessionManager as Manager
            from winsdk.windows.storage.streams import DataReader
            manager = await Manager.request_async()
            previous = None
            cover_key, cover = None, b''
            while not self.stopped.is_set():
                session = manager.get_current_session()
                if session is None:
                    if previous is not None:
                        self.snapshot = {}
                        emit('media', '', {})
                    previous = None
                    await asyncio.sleep(1)
                    continue
                try:
                    properties = await session.try_get_media_properties_async()
                    playback = session.get_playback_info()
                    timeline = session.get_timeline_properties()
                    key = (properties.title, properties.artist, properties.album_title)
                    if key != cover_key:
                        cover_key, cover = key, b''
                        if properties.thumbnail:
                            stream = await properties.thumbnail.open_read_async()
                            try:
                                if 0 < stream.size <= 1024 * 1024:
                                    reader = DataReader(stream.get_input_stream_at(0))
                                    try:
                                        await reader.load_async(stream.size)
                                        buffer = bytearray(stream.size)
                                        reader.read_bytes(buffer)
                                        cover = bytes(buffer)
                                    finally:
                                        reader.close()
                            finally:
                                stream.close()
                    playing = int(playback.playback_status) == 4
                    duration = max(0, (timeline.end_time - timeline.start_time).total_seconds())
                    position = max(0, (timeline.position - timeline.start_time).total_seconds())
                    if playing:
                        updated = timeline.last_updated_time
                        if updated.tzinfo is None:
                            updated = updated.replace(tzinfo=dt.timezone.utc)
                        elapsed = (dt.datetime.now(dt.timezone.utc) - updated).total_seconds()
                        if 0 <= elapsed < 86400:
                            position += elapsed
                    position = min(position, duration) if duration else position
                    payload = {'title': properties.title or 'Media', 'artist': properties.artist or '',
                               'album': properties.album_title or '', 'playing': playing,
                               'position': position, 'duration': duration, 'updated': time.monotonic(),
                               'cover': cover, 'source': session.source_app_user_model_id}
                    self.snapshot = payload
                    signature = (key, playing, round(position), duration)
                    if signature != previous:
                        previous = signature
                        emit('media', payload['title'], payload)
                except Exception as exc:
                    emit('service_status', f'Media belum tersedia: {exc}', {'service': 'media'})
                await asyncio.sleep(1)
        except Exception as exc:
            emit('service_status', f'Integrasi media: {exc}', {'service': 'media'})

    def stop(self):
        self.stopped.set()
        if self.thread:
            self.thread.join(timeout=1.2)


class AudioService:
    def __init__(self):
        self.stopped = threading.Event()
        self.thread = None
        self.commands = queue.Queue(maxsize=32)
        self.snapshot = {}

    def start(self):
        self.thread = threading.Thread(target=self._run, name='Kai audio', daemon=True)
        self.thread.start()

    def set_volume(self, value):
        try:
            self.commands.put_nowait(('volume', max(0, min(100, int(value)))))
        except queue.Full:
            pass

    def toggle_mute(self):
        try:
            self.commands.put_nowait(('mute', None))
        except queue.Full:
            pass

    def _run(self):
        endpoint, callback = None, None
        try:
            sys.coinit_flags = 0
            import comtypes
            comtypes.CoInitializeEx(0)
            from pycaw.pycaw import AudioUtilities
            from pycaw.callbacks import AudioEndpointVolumeCallback
            service = self
            class Callback(AudioEndpointVolumeCallback):
                def on_notify(self, new_volume, new_mute, context, channels, volumes):
                    data = dict(service.snapshot, level=round(new_volume * 100), mute=bool(new_mute))
                    service.snapshot = data
                    emit('volume', f"Volume {data['level']}%", data)
            device_id, prior_devices = None, None
            callback = Callback()
            while not self.stopped.is_set():
                try:
                    device = AudioUtilities.GetSpeakers()
                    if device.id != device_id:
                        if endpoint:
                            endpoint.UnregisterControlChangeNotify(callback)
                        device_id = device.id
                        endpoint = device.EndpointVolume
                        self.snapshot = {'level': round(endpoint.GetMasterVolumeLevelScalar() * 100),
                                         'mute': bool(endpoint.GetMute()), 'device': device.FriendlyName}
                        endpoint.RegisterControlChangeNotify(callback)
                        emit('audio_state', device.FriendlyName, self.snapshot)
                    devices = {d.id: d.FriendlyName for d in AudioUtilities.GetAllDevices()
                               if int(d.state.value if hasattr(d.state, 'value') else d.state) == 1}
                    if prior_devices is not None:
                        for identifier in devices.keys() - prior_devices.keys():
                            emit('device', 'Audio device connected', {'name': devices[identifier], 'connected': True})
                        for identifier in prior_devices.keys() - devices.keys():
                            emit('device', 'Audio device disconnected', {'name': prior_devices[identifier], 'connected': False})
                    prior_devices = devices
                    while not self.commands.empty():
                        action, value = self.commands.get_nowait()
                        if action == 'volume':
                            endpoint.SetMasterVolumeLevelScalar(value / 100, None)
                        else:
                            endpoint.SetMute(not endpoint.GetMute(), None)
                except Exception as exc:
                    emit('service_status', f'Audio: {exc}', {'service': 'audio'})
                self.stopped.wait(0.5)
        except Exception as exc:
            emit('service_status', f'Audio integration: {exc}', {'service': 'audio'})
        finally:
            if endpoint and callback:
                try:
                    endpoint.UnregisterControlChangeNotify(callback)
                except Exception:
                    pass
            try:
                comtypes.CoUninitialize()
            except (UnboundLocalError, AttributeError):
                pass

    def stop(self):
        self.stopped.set()
        if self.thread:
            self.thread.join(timeout=1)
