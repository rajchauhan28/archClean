import pytest
import asyncio
from unittest.mock import MagicMock, patch
from archclean.tui_analyzer import LargeFilesApp
from textual.widgets import SelectionList, Label

@pytest.fixture
def mock_subprocess():
    with patch("subprocess.run") as mock:
        yield mock

@pytest.fixture
def mock_remove():
    with patch("os.remove") as mock:
        yield mock

@pytest.mark.asyncio
async def test_app_scan_and_delete(mock_subprocess, mock_remove):
    # Setup mock return for scan
    # Output format: "size_in_bytes path"
    mock_subprocess.return_value.stdout = "2048 /tmp/another_file\n1024 /tmp/fake_large_file"
    mock_subprocess.return_value.returncode = 0
    
    app = LargeFilesApp(target_path="/tmp/test", limit=10)
    
    async with app.run_test() as pilot:
        # Wait for the worker to populate the list.
        # Check condition in a loop
        for _ in range(10):
            if "hidden" not in app.query_one("#file-list").classes:
                break
            await asyncio.sleep(0.1)
        else:
            pytest.fail("Timeout waiting for file list to appear")
        
        file_list = app.query_one("#file-list", SelectionList)
        assert len(file_list.options) == 2
        
        # Verify options are correct
        assert file_list.options[0].value == "/tmp/another_file"
        assert file_list.options[1].value == "/tmp/fake_large_file"
        
        # Test Deletion
        # Select the second file
        file_list.select("/tmp/fake_large_file")
        
        # Click Delete button
        await pilot.click("#btn-delete")
        
        # Wait for UI update (deletion logic runs in main thread or worker? In this app it is in main thread)
        # But it calls scan_files again which is a worker.
        await pilot.pause()
        
        # Verify os.remove was called
        mock_remove.assert_called_with("/tmp/fake_large_file")
        
        # We assume the status update works if the code reached here without error.

