import unittest
from unittest.mock import patch, MagicMock
from archclean.cleaners import home
from pathlib import Path

class TestHome(unittest.TestCase):

    @patch('archclean.cleaners.home.shutil.rmtree')
    @patch('archclean.cleaners.home.tracker')
    @patch('archclean.cleaners.home.confirm_action')
    @patch('archclean.cleaners.home.get_home_dir')
    def test_clean_thumbnails(self, mock_home, mock_confirm, mock_tracker, mock_rmtree):
        # Setup mock home and thumbnail dir
        mock_path = MagicMock()
        mock_home.return_value = mock_path
        mock_thumb_dir = mock_path / ".cache" / "thumbnails"
        mock_thumb_dir.exists.return_value = True
        
        # Simulate file iteration for size calc
        mock_file = MagicMock()
        mock_file.is_file.return_value = True
        mock_file.stat.return_value.st_size = 1024 * 1024 * 5 # 5MB
        mock_thumb_dir.rglob.return_value = [mock_file]
        
        mock_confirm.return_value = True
        
        home.clean_thumbnails()
        
        mock_rmtree.assert_called()
        mock_tracker.add.assert_called_with("Home", "Thumbnails", "Cleaned", "Freed 5.00 MB")
