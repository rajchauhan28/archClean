from textual.app import App, ComposeResult
from textual.widgets import Header, Footer, SelectionList, Button, Label, LoadingIndicator, Static
from textual.containers import Container, Horizontal, Vertical
from textual.screen import Screen
from textual.worker import Worker
from textual import work
import sh
import os
from pathlib import Path
from archclean.utils import run_command
from rich.filesize import decimal

class LargeFilesApp(App):
    CSS = """
    Screen {
        layout: vertical;
    }
    #list-container {
        height: 1fr;
        border: solid green;
    }
    #status-bar {
        height: auto;
        dock: bottom;
        background: $primary-background;
        padding: 1;
    }
    #buttons {
        height: auto;
        dock: bottom;
        align: center middle;
        padding: 1;
    }
    Button {
        margin: 1;
    }
    .hidden {
        display: none;
    }
    """

    BINDINGS = [
        ("q", "quit", "Quit"),
        ("d", "delete_selected", "Delete Selected"),
        ("r", "refresh", "Refresh")
    ]

    def __init__(self, target_path="/", limit=100, sudo=False):
        super().__init__()
        self.target_path = target_path
        self.limit = limit
        self.sudo = sudo
        self.files_map = {}  # Map value to (path, size)

    def compose(self) -> ComposeResult:
        yield Header()
        yield Container(
            LoadingIndicator(id="loading"),
            SelectionList(id="file-list", classes="hidden"),
            id="list-container"
        )
        yield Label("", id="status")
        yield Horizontal(
            Button("Delete Selected", variant="error", id="btn-delete"),
            Button("Quit", variant="primary", id="btn-quit"),
            id="buttons"
        )
        yield Footer()

    def on_mount(self) -> None:
        self.scan_files()

    @work(exclusive=True, thread=True)
    def scan_files(self) -> None:
        self.query_one("#status", Label).update(f"Scanning {self.target_path} for top {self.limit} large files...")
        self.call_from_thread(self.query_one("#loading").remove_class, "hidden")
        self.call_from_thread(self.query_one("#file-list").add_class, "hidden")
        
        try:
from textual.app import App, ComposeResult
from textual.widgets import Header, Footer, SelectionList, Button, Label, LoadingIndicator, Static
from textual.containers import Container, Horizontal, Vertical
from textual.screen import Screen
from textual.worker import Worker
from textual import work
import sh
import os
import subprocess
from pathlib import Path
from archclean.utils import run_command
from rich.filesize import decimal

class LargeFilesApp(App):
    CSS = """
    Screen {
        layout: vertical;
    }
    #list-container {
        height: 1fr;
        border: solid green;
    }
    #status-bar {
        height: auto;
        dock: bottom;
        background: $primary-background;
        padding: 1;
    }
    #buttons {
        height: auto;
        dock: bottom;
        align: center middle;
        padding: 1;
    }
    Button {
        margin: 1;
    }
    .hidden {
        display: none;
    }
    """

    BINDINGS = [
        ("q", "quit", "Quit"),
        ("d", "delete_selected", "Delete Selected"),
        ("r", "refresh", "Refresh")
    ]

    def __init__(self, target_path="/", limit=100, sudo=False):
        super().__init__()
        self.target_path = target_path
        self.limit = limit
        self.sudo = sudo
        self.files_map = {}  # Map value to (path, size)

    def compose(self) -> ComposeResult:
        yield Header()
        yield Container(
            LoadingIndicator(id="loading"),
            SelectionList(id="file-list", classes="hidden"),
            id="list-container"
        )
        yield Label("", id="status")
        yield Horizontal(
            Button("Delete Selected", variant="error", id="btn-delete"),
            Button("Quit", variant="primary", id="btn-quit"),
            id="buttons"
        )
        yield Footer()

    def on_mount(self) -> None:
        self.scan_files()

    @work(exclusive=True, thread=True)
    def scan_files(self) -> None:
        self.query_one("#status", Label).update(f"Scanning {self.target_path} for top {self.limit} large files...")
        self.call_from_thread(self.query_one("#loading").remove_class, "hidden")
        self.call_from_thread(self.query_one("#file-list").add_class, "hidden")
        
        try:
            # find <path> -xdev -type f -printf "%s %p\n" | sort -rn | head -n <limit>
            # 2>/dev/null to silence permission denied errors if not sudo
            cmd_str = f"find {self.target_path} -xdev -type f -printf '%s %p\n' 2>/dev/null | sort -rn | head -n {self.limit}"
            
            if self.sudo:
                cmd_str = f"sudo {cmd_str}"

            # Run the command using subprocess
            result = subprocess.run(
                cmd_str, 
                shell=True, 
                stdout=subprocess.PIPE, 
                stderr=subprocess.PIPE, 
                text=True
            )

            if result.returncode != 0:
                 raise Exception(f"Scan failed: {result.stderr}")

            output = result.stdout
            
            items = []
            self.files_map = {}
            
            for line in output.strip().split('\n'):
                if not line: continue
                parts = line.split(' ', 1)
                if len(parts) != 2: continue
                
                try:
                    size_bytes = int(parts[0])
                    path = parts[1]
                except ValueError:
                    continue
                
                human_size = decimal(size_bytes)
                display_text = f"{human_size} | {path}"
                
                # Use path as the value
                items.append((display_text, path))
                self.files_map[path] = size_bytes

            self.call_from_thread(self.update_list, items)

        except Exception as e:
            self.call_from_thread(self.query_one("#status", Label).update, f"Error: {str(e)}")

    def update_list(self, items):
        self.query_one("#loading").add_class("hidden")
        file_list = self.query_one("#file-list", SelectionList)
        file_list.clear_options()
        for label, value in items:
            file_list.add_option((label, value))
        file_list.remove_class("hidden")
        self.query_one("#status", Label).update(f"Found {len(items)} files.")
        file_list.focus()

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "btn-quit":
            self.exit()
        elif event.button.id == "btn-delete":
            self.action_delete_selected()

    def action_delete_selected(self) -> None:
        file_list = self.query_one("#file-list", SelectionList)
        selected = file_list.selected
        
        if not selected:
            self.query_one("#status", Label).update("No files selected.")
            return
        
        count = 0
        failed = 0
        for path in selected:
            try:
                # Remove file
                if self.sudo:
                    run_command("rm", ["-f", path], sudo=True)
                else:
                    os.remove(path)
                count += 1
            except Exception:
                # Try sudo if failed?
                if not self.sudo:
                     if run_command("rm", ["-f", path], sudo=True):
                         count += 1
                     else:
                         failed += 1
                else:
                    failed += 1
        
        self.query_one("#status", Label).update(f"Deleted {count} files. {failed} failed.")
        
        # Refresh list
        self.scan_files()

            
            items = []
            self.files_map = {}
            
            for line in output.strip().split('\n'):
                if not line: continue
                parts = line.split(' ', 1)
                if len(parts) != 2: continue
                
                size_bytes = int(parts[0])
                path = parts[1]
                
                human_size = decimal(size_bytes)
                display_text = f"{human_size} | {path}"
                
                # Use path as the value
                items.append((display_text, path))
                self.files_map[path] = size_bytes

            self.call_from_thread(self.update_list, items)

        except Exception as e:
            self.call_from_thread(self.query_one("#status", Label).update, f"Error: {str(e)}")

    def update_list(self, items):
        self.query_one("#loading").add_class("hidden")
        file_list = self.query_one("#file-list", SelectionList)
        file_list.clear_options()
        for label, value in items:
            file_list.add_option((label, value))
        file_list.remove_class("hidden")
        self.query_one("#status", Label).update(f"Found {len(items)} files.")
        file_list.focus()

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "btn-quit":
            self.exit()
        elif event.button.id == "btn-delete":
            self.action_delete_selected()

    def action_delete_selected(self) -> None:
        file_list = self.query_one("#file-list", SelectionList)
        selected = file_list.selected
        
        if not selected:
            self.query_one("#status", Label).update("No files selected.")
            return

        # In a real TUI, we might want a confirmation modal. 
        # For simplicity, we just delete or could add a "Confirm" step.
        # Let's add a simple text update to confirm.
        
        # NOTE: Textual 0.x/1.x has ModalScreens. 
        # For now, let's just delete and show status, as requested "mark deletable".
        
        count = 0
        failed = 0
        for path in selected:
            try:
                # Remove file
                if self.sudo:
                    run_command("rm", ["-f", path], sudo=True)
                else:
                    os.remove(path)
                count += 1
            except Exception:
                # Try sudo if failed?
                if not self.sudo:
                     if run_command("rm", ["-f", path], sudo=True):
                         count += 1
                     else:
                         failed += 1
                else:
                    failed += 1
        
        self.query_one("#status", Label).update(f"Deleted {count} files. {failed} failed.")
        
        # Refresh list
        self.scan_files()
