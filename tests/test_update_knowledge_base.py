import copy
import json
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
import update_knowledge_base as u


class SnapshotTests(unittest.TestCase):
    def setUp(self):
        self.song = {'title': 'Test', 'artist': 'Artist', 'category': '舞萌',
                     'version': '舞萌DX 2026', 'lev_bas': '4'}
        self.detail = {'source': 'divingfish', 'songId': '1', 'songTitle': 'Test',
                       'artist': 'Artist', 'sheetType': 'std', 'difficulty': 'basic',
                       'level': '4', 'internalLevelValue': 4.0, 'notes': {'tap': 10},
                       'noteDesigner': '-'}

    def build(self, details=None, aliases=None):
        details = [self.detail] if details is None else details
        def fetch(url, timeout):
            if url == u.CN_MAIDATA_URL:
                return [self.song]
            if url == u.ALIAS_URL:
                if aliases is None:
                    raise RuntimeError('alias offline')
                return aliases
            if url == u.DIVING_FISH_MUSIC_URL:
                return [{}]
            raise AssertionError(url)
        with patch.object(u, 'fetch_json', side_effect=fetch), \
             patch.object(u, 'detail_rows_from_divingfish', return_value=details), \
             patch.object(u, 'fetch_text', return_value=''), \
             patch.object(u, 'load_annotations', return_value={}), \
             patch.object(u, 'load_old_rows', return_value=[{
                 'title': 'Test', 'artist': 'Artist', 'type': 'standard',
                 'difficulty': 'basic', 'aliases': ['Old alias'], 'chart_tags': ['交互'],
                 'ds': 4.0, 'id': 1} ]):
            return u.build_snapshot(1)

    def test_alias_failure_keeps_alias_and_chart_tags(self):
        songs, rows = self.build()
        self.assertIn('Old alias', songs[0]['aliases'])
        self.assertEqual(rows[0]['chart_tags'], ['交互'])
        u.validate_snapshot(songs, rows)

    def test_new_alias_merges_instead_of_replacing(self):
        songs, _ = self.build(aliases={'code': 0, 'content': [{'SongID': 1, 'Alias': ['New alias']}]})
        self.assertTrue({'Old alias', 'New alias'} <= set(songs[0]['aliases']))

    def test_conflicting_detail_does_not_restore_stale_ds(self):
        detail = dict(self.detail, internalLevelValue=5.0)
        _, rows = self.build([detail])
        self.assertIsNone(rows[0]['ds'])

    def test_wrong_artist_is_not_matched(self):
        detail = dict(self.detail, artist='Other artist')
        self.assertIsNone(u.choose_group(self.song, 'std', {'Test': [detail]}, [detail]))

    def test_tied_candidates_are_unresolved(self):
        other = dict(self.detail, songId='2')
        self.assertIsNone(u.choose_group(self.song, 'std', {'Test': [self.detail, other]}, []))

    def test_empty_cn_refuses_write(self):
        with patch.object(u, 'fetch_json', return_value=[]):
            with self.assertRaises(ValueError):
                u.build_snapshot(1)

    def test_rejects_missing_duplicate_chart_and_bad_ds(self):
        songs, rows = self.build()
        for invalid in ([], rows + rows, [dict(rows[0], ds=6.0)], [dict(rows[0], id=2)]):
            with self.subTest(invalid=invalid):
                with self.assertRaises(ValueError):
                    u.validate_snapshot(songs, invalid)

    def test_committed_snapshot_and_link_disambiguation(self):
        songs = json.loads(u.SONGS_FILE.read_text())
        rows = u.load_old_rows()
        u.validate_snapshot(songs, rows)
        self.assertEqual((len(songs), len(rows)), (1293, 5516))
        self.assertEqual({s['std_id'] for s in songs if s['title'] == 'Link'}, {131, 383})
        self.assertTrue(all(r['id'] is not None for r in rows))

    def test_ds_threshold_and_nonfinite_values(self):
        self.assertEqual(u.ds_label(12.6), '12')
        self.assertEqual(u.ds_label(12.7), '12+')
        for value in (None, 'bad', float('nan'), float('inf'), 0):
            self.assertIsNone(u.ds_label(value))

    def test_offline_render_is_repeatable(self):
        songs = json.loads(u.SONGS_FILE.read_text())
        rows = u.load_old_rows()
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            with patch.object(u, 'SONGS_FILE', root / 'songs.json'), \
                 patch.object(u, 'LEVEL_INDEX', root / 'level_index.json'), \
                 patch.object(u, 'KB_DIR', root / 'knowledge_base'):
                u.write_snapshot(songs, rows)
                first = {str(p.relative_to(root)): p.read_bytes() for p in root.rglob('*') if p.is_file()}
                u.write_snapshot(songs, rows)
                second = {str(p.relative_to(root)): p.read_bytes() for p in root.rglob('*') if p.is_file()}
                self.assertEqual(first, second)


if __name__ == '__main__':
    unittest.main()
