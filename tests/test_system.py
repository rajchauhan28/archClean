import unittest
from unittest.mock import patch, MagicMock
from archclean.cleaners import system

class TestSystem(unittest.TestCase):

    @patch('archclean.cleaners.system.run_command')
    @patch('archclean.cleaners.system.tracker')
    @patch('archclean.cleaners.system.Confirm.ask')
    @patch('archclean.cleaners.system.sh.Command')
    @patch('pathlib.Path')
    @patch('archclean.cleaners.system.confirm_action')
    def test_clean_pacman_cache(self, mock_confirm, mock_path, mock_command, mock_ask, mock_tracker, mock_run):
        # Mock pacman-conf output
        mock_pacman_conf = MagicMock()
        mock_pacman_conf.return_value = "/var/cache/pacman/pkg/"
        mock_command.return_value = mock_pacman_conf
        
        # Mock Path existence and scanning
        mock_dir = MagicMock()
        mock_dir.exists.return_value = True
        mock_dir.is_dir.return_value = True
        
        # Determine behavior of iterdir: one broken dir, one file
        mock_broken = MagicMock()
        mock_broken.is_dir.return_value = True
        mock_broken.__str__.return_value = "/var/cache/pacman/pkg/broken_dir"
        
        mock_file = MagicMock()
        mock_file.is_dir.return_value = False
        
        mock_dir.iterdir.return_value = [mock_broken, mock_file]
        
        mock_path.return_value = mock_dir
        
        # Set all confirmations to True
        mock_ask.return_value = True # thorough
        mock_confirm.return_value = True # remove broken, clean cache
        
        mock_run.return_value = True
        
        system.clean_pacman_cache(force=False)
        
        # Check if we tried to remove the broken dir
        mock_run.assert_any_call("rm", ["-rf", "/var/cache/pacman/pkg/broken_dir"], sudo=True)
        # Check if we ran the main pacman command
        mock_run.assert_any_call("pacman", ["-Scc"], sudo=True)
        mock_tracker.add.assert_called()

    @patch('archclean.cleaners.system.run_command')
    @patch('archclean.cleaners.system.tracker')
    @patch('archclean.cleaners.system.confirm_action')
    def test_vacuum_journal(self, mock_confirm, mock_tracker, mock_run):
        mock_confirm.return_value = True
        mock_run.return_value = True
        
        system.vacuum_journal()
        
        mock_run.assert_called_with("journalctl", ["--vacuum-time=2weeks"], sudo=True)
        mock_tracker.add.assert_called_with("System", "Journal", "Cleaned", "Vacuumed to 2 weeks")

    @patch('archclean.cleaners.system.run_command')
    @patch('archclean.cleaners.system.tracker')
    @patch('archclean.cleaners.system.confirm_action')
    @patch('archclean.cleaners.system.sh.pacman')
    def test_remove_orphans(self, mock_pacman, mock_confirm, mock_tracker, mock_run):
        # Simulate output with color codes
        mock_pacman.return_value = "\x1b[31mpackage1\x1b[0m\npackage2"
        mock_confirm.return_value = True
        mock_run.return_value = True
        
        system.remove_orphans()
        
        # Check if stripping worked and proper command was called
        mock_run.assert_called_with("pacman", ["-Rns", "package1", "package2"], sudo=True)
        mock_tracker.add.assert_called_with("System", "Orphans", "Cleaned", "Removed 2 packages")