"""Bounded LRCLIB matching, missing catalog entries and retry behavior."""
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
from urllib.error import HTTPError

import integrations


class LyricsTests(unittest.TestCase):
    def setUp(self):
        self.directory = tempfile.TemporaryDirectory()
        self.addCleanup(self.directory.cleanup)
        self.patch = patch('integrations.data_dir', return_value=Path(self.directory.name))
        self.patch.start()
        self.addCleanup(self.patch.stop)

    @staticmethod
    def missing():
        return HTTPError('https://lrclib.net/api/get', 404, 'Not Found', {}, None)

    def test_missing_is_cached_briefly_then_retried(self):
        with patch('integrations.fetch_json', side_effect=[self.missing(), []]) as fetch:
            self.assertEqual(integrations.lyrics('Fixture', 'Artist', 120)['status'], 'unavailable')
            self.assertEqual(integrations.lyrics('Fixture', 'Artist', 120)['status'], 'unavailable')
            self.assertEqual(fetch.call_count, 2)
        with patch('integrations.time.time', return_value=10**12), patch('integrations.fetch_json', side_effect=[self.missing(), []]) as fetch:
            integrations.lyrics('Fixture', 'Artist', 120)
            self.assertEqual(fetch.call_count, 2)

    def test_search_accepts_only_matching_title_artist_and_duration(self):
        record = {'trackName': 'Fixture!', 'artistName': 'ARTIST', 'duration': 121,
                  'plainLyrics': 'Synthetic fixture text', 'syncedLyrics': '[00:01]Synthetic fixture text'}
        with patch('integrations.fetch_json', side_effect=[self.missing(), [record]]):
            result = integrations.lyrics('Fixture', 'Artist', 120)
        self.assertEqual(result['status'], 'available')
        self.assertEqual(result['synced'][0][0], 1)
        with patch('integrations.fetch_json') as fetch:
            self.assertEqual(integrations.lyrics('Fixture', 'Artist', 120), result)
            fetch.assert_not_called()

    def test_search_rejects_other_artist_version_or_duration(self):
        records = [dict(trackName=title, artistName=artist, duration=duration, plainLyrics='Fixture')
                   for title, artist, duration in [('Fixture', 'Other', 120), ('Fixture Live', 'Artist', 120), ('Fixture', 'Artist', 150)]]
        with patch('integrations.fetch_json', side_effect=[self.missing(), records]):
            self.assertEqual(integrations.lyrics('Fixture', 'Artist', 120)['status'], 'unavailable')

    def test_instrumental_and_empty_records_are_not_blank_lyrics(self):
        with patch('integrations.fetch_json', return_value={'instrumental': True}):
            self.assertEqual(integrations.lyrics('Instrumental', 'Artist')['status'], 'instrumental')
        with patch('integrations.fetch_json', return_value={}):
            self.assertEqual(integrations.lyrics('Empty', 'Artist')['status'], 'unavailable')

    def test_corrupt_cache_is_refetched_and_service_failure_retries_later(self):
        with patch('integrations.fetch_json', return_value={'plainLyrics': 'Fixture'}):
            integrations.lyrics('Fixture', 'Artist')
        next(Path(self.directory.name).rglob('*.json')).write_text('{broken', encoding='utf-8')
        error = HTTPError('https://lrclib.net', 503, 'Unavailable', {}, None)
        with patch('integrations.fetch_json', side_effect=error) as fetch:
            self.assertEqual(integrations.lyrics('Fixture', 'Artist')['status'], 'retry')
            integrations.lyrics('Fixture', 'Artist')
            self.assertEqual(fetch.call_count, 1)
        with patch('integrations.time.time', return_value=10**12), patch('integrations.fetch_json', return_value={'plainLyrics': 'Fixture'}):
            self.assertEqual(integrations.lyrics('Fixture', 'Artist')['status'], 'available')


if __name__ == '__main__':
    unittest.main()
