import os
import sqlite3
import tempfile
import unittest
from datetime import datetime, timedelta
from unittest.mock import patch

import history_reader
import decision_engine
from focus_daemon import applescript_string


class RecentDoomscrollLoopTests(unittest.TestCase):
    def test_ignores_distractions_outside_window(self):
        fd, history_path = tempfile.mkstemp(suffix=".sqlite")
        os.close(fd)
        try:
            connection = sqlite3.connect(history_path)
            connection.execute(
                "CREATE TABLE urls "
                "(url TEXT, title TEXT, visit_count INTEGER, last_visit_time INTEGER)"
            )

            chrome_epoch = 11644473600
            now = datetime.now()

            def chrome_timestamp(value):
                return int((value.timestamp() + chrome_epoch) * 1_000_000)

            visits = [
                ("https://youtube.com/watch?v=1", "Recent video", 1, now - timedelta(minutes=2)),
                ("https://reddit.com/r/test", "Recent thread", 1, now - timedelta(minutes=8)),
                ("https://instagram.com/reel/1", "Recent reel", 1, now - timedelta(minutes=14)),
                ("https://twitch.tv/old", "Old stream", 1, now - timedelta(minutes=40)),
            ]
            connection.executemany(
                "INSERT INTO urls VALUES (?, ?, ?, ?)",
                [
                    (url, title, count, chrome_timestamp(visited_at))
                    for url, title, count, visited_at in visits
                ],
            )
            connection.commit()
            connection.close()

            with patch.object(history_reader, "HISTORY_PATHS", [("Test", history_path)]):
                triggered, count = history_reader.check_recent_doomscroll_loop(
                    threshold_count=3,
                    window_minutes=15,
                )

            self.assertTrue(triggered)
            self.assertEqual(count, 3)
        finally:
            os.unlink(history_path)


class NotificationSafetyTests(unittest.TestCase):
    def test_applescript_string_escapes_quotes_backslashes_and_newlines(self):
        value = applescript_string('A "quoted" path\\name\nnext', limit=100)
        self.assertEqual(value, '"A \\"quoted\\" path\\\\name next"')

    def test_applescript_string_limits_untrusted_text(self):
        self.assertEqual(len(applescript_string("x" * 500)), 122)


class MemoryModeTests(unittest.TestCase):
    def test_neural_model_is_opt_in(self):
        with patch.dict(os.environ, {}, clear=False):
            os.environ.pop("FOCUS_ENABLE_JEV_MODEL", None)
            self.assertIsNone(decision_engine.get_jev_decider())


if __name__ == "__main__":
    unittest.main()
