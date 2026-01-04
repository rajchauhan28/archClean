import unittest
from unittest.mock import patch, MagicMock
from archclean import analyzer
import os

class TestAnalyzer(unittest.TestCase):

    @patch('archclean.analyzer.check_binary')
    @patch('archclean.analyzer.confirm_action')
    @patch('archclean.analyzer.run_command')
    @patch('archclean.analyzer.os.path.expanduser')
    def test_analyze_home_success(self, mock_expanduser, mock_run, mock_confirm, mock_check_binary):
        # Setup
        mock_check_binary.return_value = True # ncdu installed
        mock_confirm.side_effect = [True, False] # Yes to Home, No to Root
        mock_expanduser.return_value = "/home/testuser"
        
        # Execute
        analyzer.analyze_disk_usage(force=False)
        
        # Verify
        mock_check_binary.assert_called_with("ncdu")
        mock_expanduser.assert_called_with("~")
        
        # Verify run_command called for home
        mock_run.assert_any_call("ncdu", ["/home/testuser"])
        
        # Verify not called for root
        # We can check the calls list
        calls = mock_run.call_args_list
        self.assertEqual(len(calls), 1)
        self.assertEqual(calls[0][0][0], "ncdu")
        self.assertEqual(calls[0][0][1], ["/home/testuser"])

    @patch('archclean.analyzer.check_binary')
    @patch('archclean.analyzer.confirm_action')
    @patch('archclean.analyzer.run_command')
    def test_analyze_root_success(self, mock_run, mock_confirm, mock_check_binary):
        # Setup
        mock_check_binary.return_value = True # ncdu installed
        mock_confirm.side_effect = [False, True] # No to Home, Yes to Root
        
        # Execute
        analyzer.analyze_disk_usage(force=False)
        
        # Verify
        mock_run.assert_called_with("ncdu", ["/", "-x"], sudo=True)

    @patch('archclean.analyzer.check_binary')
    @patch('archclean.analyzer.confirm_action')
    @patch('archclean.analyzer.run_command')
    def test_analyze_ncdu_missing_install_declined(self, mock_run, mock_confirm, mock_check_binary):
        # Setup
        mock_check_binary.return_value = False # ncdu missing
        mock_confirm.return_value = False # Decline install
        
        # Execute
        analyzer.analyze_disk_usage()
        
        # Verify
        mock_run.assert_not_called()

    @patch('archclean.analyzer.check_binary')
    @patch('archclean.analyzer.confirm_action')
    @patch('archclean.analyzer.run_command')
    def test_analyze_ncdu_install_flow(self, mock_run, mock_confirm, mock_check_binary):
        # Setup
        # First check fails (not installed), second check passes (installed after command)
        mock_check_binary.side_effect = [False, True, True] 
        # Confirm install (True), then Confirm Home (False), Confirm Root (False)
        mock_confirm.side_effect = [True, False, False]
        
        # Execute
        analyzer.analyze_disk_usage()
        
        # Verify install command was run
        mock_run.assert_any_call("pacman", ["-S", "ncdu"], sudo=True)
