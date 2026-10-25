import os
import tempfile
import unittest
from unittest.mock import patch

import quota_manager


class QuotaPersistenceTests(unittest.TestCase):
    def test_empty_quota_file_is_reinitialized(self):
        fd, quota_path = tempfile.mkstemp(suffix=".json")
        os.close(fd)
        try:
            with patch.object(quota_manager, "QUOTA_FILE", quota_path):
                summary = quota_manager.set_quota_limits(1, 1)
                self.assertEqual(summary["episodes_max"], 1)
                self.assertEqual(summary["movies_max"], 1)
                self.assertEqual(summary["episodes_used"], 0)
        finally:
            os.unlink(quota_path)

    def test_save_quota_never_leaves_partial_json(self):
        fd, quota_path = tempfile.mkstemp(suffix=".json")
        os.close(fd)
        try:
            with patch.object(quota_manager, "QUOTA_FILE", quota_path):
                quota_manager.save_quota(
                    {
                        "date": quota_manager.get_today_str(),
                        "max_episodes": 2,
                        "max_movies": 1,
                        "episodes_watched": [],
                        "movies_watched": [],
                    }
                )
                with open(quota_path, "r", encoding="utf-8") as quota_file:
                    self.assertIn('"max_episodes": 2', quota_file.read())
        finally:
            os.unlink(quota_path)


if __name__ == "__main__":
    unittest.main()
