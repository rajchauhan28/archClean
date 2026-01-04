import unittest
from unittest.mock import patch, MagicMock
from archclean.cleaners import languages

class TestLanguages(unittest.TestCase):

    @patch('archclean.cleaners.languages.tracker')
    @patch('archclean.cleaners.languages.check_binary')
    @patch('archclean.cleaners.languages.confirm_action')
    @patch('archclean.cleaners.languages.run_command')
    def test_clean_python_cache(self, mock_run, mock_confirm, mock_check, mock_tracker):
        mock_check.side_effect = lambda x: True # python, pip both exist
        mock_confirm.return_value = True
        mock_run.return_value = True
        
        languages.clean_python_cache()
        
        mock_run.assert_called_with("pip", ["cache", "purge"])
        mock_tracker.add.assert_called()

    @patch('archclean.cleaners.languages.tracker')
    @patch('archclean.cleaners.languages.check_binary')
    @patch('archclean.cleaners.languages.confirm_action')
    @patch('archclean.cleaners.languages.run_command')
    @patch('shutil.rmtree')
    @patch('pathlib.Path')
    def test_clean_bun_cache(self, mock_path, mock_rmtree, mock_run, mock_confirm, mock_check, mock_tracker):
        mock_check.return_value = True
        mock_confirm.return_value = True
        
        # Setup mock path
        mock_bun_cache = MagicMock()
        mock_bun_cache.exists.return_value = True
        
        # We need to mock the chain Path.home() / ".bun" / "install" / "cache"
        # Path.home() returns a new path object, and subsequent / operators return new path objects
        mock_home = MagicMock()
        mock_path.home.return_value = mock_home
        
        # Mocking the / operator (div)
        mock_home.__truediv__.return_value.__truediv__.return_value.__truediv__.return_value = mock_bun_cache
        
        languages.clean_bun_cache()
        
        # Verify rmtree was called with the final path object
        mock_rmtree.assert_called_with(mock_bun_cache)
        mock_tracker.add.assert_called()

    @patch('archclean.cleaners.languages.tracker')
    @patch('archclean.cleaners.languages.check_binary')
    @patch('archclean.cleaners.languages.confirm_action')
    @patch('archclean.cleaners.languages.run_command')
    def test_clean_docker_cache(self, mock_run, mock_confirm, mock_check, mock_tracker):
        mock_check.return_value = True
        mock_confirm.return_value = True
        mock_run.return_value = True
        
        languages.clean_docker_cache(force=True)
        
        mock_run.assert_called_with("docker", ["system", "prune", "--force"])
        mock_tracker.add.assert_called()

    @patch('archclean.cleaners.languages.tracker')
    @patch('archclean.cleaners.languages.check_binary')
    @patch('archclean.cleaners.languages.confirm_action')
    @patch('archclean.cleaners.languages.run_command')
    def test_clean_ccache(self, mock_run, mock_confirm, mock_check, mock_tracker):
        mock_check.return_value = True
        mock_confirm.return_value = True
        mock_run.return_value = True
        
        languages.clean_ccache()
        
        mock_run.assert_called_with("ccache", ["-C"])
        mock_tracker.add.assert_called()

    @patch('archclean.cleaners.languages.tracker')
    @patch('archclean.cleaners.languages.check_binary')
    @patch('archclean.cleaners.languages.confirm_action')
    @patch('archclean.cleaners.languages.run_command')
    def test_clean_dotnet_cache(self, mock_run, mock_confirm, mock_check, mock_tracker):
        mock_check.return_value = True
        mock_confirm.return_value = True
        mock_run.return_value = True
        
        languages.clean_dotnet_cache()
        
        mock_run.assert_called_with("dotnet", ["nuget", "locals", "all", "--clear"])
        mock_tracker.add.assert_called()
