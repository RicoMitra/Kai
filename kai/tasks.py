"""Run optional integrations in disposable processes, keeping idle Qt memory small."""
import multiprocessing as mp
import threading
import time

def _entry(pipe, name, args):
    captured = []
    try:
        import events
        events.subscribe(lambda event: captured.append((event.kind, event.text, event.data)) if len(captured) < 16 else None)
        if name == 'command':
            from actions import run
            from intents import parse
            result = run(parse(args[0]))
        elif name == 'transform':
            from transform import convert
            result=convert(args[0])
        elif name == 'login':
            from actions import sp
            result = 'Spotify login successful' if sp().current_user() else 'Login not completed'
        elif name == 'apps':
            from quick_command import app_catalog
            result = app_catalog()
        else:
            import integrations
            if name == 'weather': result = integrations.weather(*args)
            elif name == 'lyrics': result = integrations.lyrics(*args)
            elif name == 'calendar':
                from storage import Store
                result = integrations.import_calendar(args[0], Store(args[1]))
            else: raise ValueError('Unknown task')
        try:pipe.send((True, result, captured))
        except (BrokenPipeError,EOFError,OSError):pass  # Panel cancellation already closed the receiver.
    except Exception as exc:
        try:pipe.send((False, str(exc), []))
        except (BrokenPipeError,EOFError,OSError):pass
    finally:
        pipe.close()


def invoke(name, *args, timeout=45, canceled=None):
    canceled = canceled or threading.Event()
    if canceled.is_set():
        raise RuntimeError('Task canceled when panel closed')
    context = mp.get_context('spawn')
    receive, send = context.Pipe(duplex=False)
    process = context.Process(target=_entry, args=(send, name, args), daemon=True)
    try:
        process.start()
        send.close()
        deadline = time.monotonic() + timeout
        while not receive.poll(0.1):
            if canceled.is_set():
                raise RuntimeError('Task canceled when panel closed')
            if time.monotonic() >= deadline:
                raise TimeoutError('Service timed out; worker closed')
        try:
            ok, result, captured = receive.recv()
        except EOFError:
            raise RuntimeError('Service stopped before returning a result') from None
        if not ok:
            raise RuntimeError(result)
    finally:
        send.close(); receive.close()
        if process.pid:
            process.join(timeout=0.5)
            if process.is_alive():
                process.terminate(); process.join(timeout=2)
            process.close()
        if name=='transform' and canceled.is_set():
            import shutil
            shutil.rmtree(args[0]['scratch'],ignore_errors=True)
    from events import emit
    for kind, text, data in captured:
        emit(kind, text, data)
    return result
