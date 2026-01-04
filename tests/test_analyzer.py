import unittest
from unittest.mock import patch, MagicMock
from archclean import analyzer

class TestAnalyzer(unittest.TestCase):

    @patch('rich.prompt.Prompt.ask')
    @patch('archclean.analyzer.check_binary')
    @patch('archclean.analyzer.confirm_action')
    @patch('archclean.analyzer.run_command')
    @patch('archclean.analyzer.os.path.expanduser')
    def test_analyze_home_success(self, mock_expanduser, mock_run, mock_confirm, mock_check_binary, mock_ask):
        # Setup
        mock_ask.return_value = "2" # Choose ncdu
        mock_check_binary.return_value = True # ncdu installed
        mock_confirm.return_value = False # Root? -> No (defaults to Home)
        mock_expanduser.return_value = "/home/testuser"
    
        # Execute
        analyzer.analyze_disk_usage(force=False)
    
        # Verify
        mock_run.assert_called_with("ncdu", ["/home/testuser"], sudo=False)

    @patch('rich.prompt.Prompt.ask')
    @patch('archclean.analyzer.check_binary')
    @patch('archclean.analyzer.confirm_action')
    @patch('archclean.analyzer.run_command')
    def test_analyze_root_success(self, mock_run, mock_confirm, mock_check_binary, mock_ask):
        # Setup
        mock_ask.return_value = "2" # Choose ncdu
        mock_check_binary.return_value = True # ncdu installed
        mock_confirm.return_value = True # Root? -> Yes
    
        # Execute
        analyzer.analyze_disk_usage(force=False)
    
        # Verify
        mock_run.assert_called_with("ncdu", ["/", "-x"], sudo=True)

    @patch('rich.prompt.Prompt.ask')
    @patch('archclean.analyzer.check_binary')
    @patch('archclean.analyzer.confirm_action')
    @patch('archclean.analyzer.run_command')
    def test_analyze_ncdu_missing_install_declined(self, mock_run, mock_confirm, mock_check_binary, mock_ask):
        # Setup
        mock_ask.return_value = "2" # Choose ncdu
        mock_check_binary.return_value = False # ncdu missing
        # Sequence: Root? -> No, Install? -> No
        mock_confirm.side_effect = [False, False] 
    
        # Execute
        analyzer.analyze_disk_usage()
    
        # Verify
        # Should check binary, then ask to install
        mock_check_binary.assert_called_with("ncdu")
        # Check second confirm call (Install)
        mock_confirm.assert_any_call("Do you want to install ncdu? (sudo pacman -S ncdu)", force=False)
        # Should NOT run pacman or ncdu
        assert not mock_run.called

    @patch('rich.prompt.Prompt.ask')
    @patch('archclean.analyzer.check_binary')
    @patch('archclean.analyzer.confirm_action')
    @patch('archclean.analyzer.run_command')
    def test_analyze_ncdu_install_flow(self, mock_run, mock_confirm, mock_check_binary, mock_ask):
        # Setup
        mock_ask.return_value = "2" # Choose ncdu
        # First check fails (not installed), second check passes (installed after command)
        mock_check_binary.side_effect = [False, True, True]
        # Sequence: Root? -> No, Install? -> Yes
        mock_confirm.side_effect = [False, True]
    
        # Execute
        analyzer.analyze_disk_usage()
    
        # Verify
        mock_run.assert_any_call("pacman", ["-S", "ncdu"], sudo=True)
