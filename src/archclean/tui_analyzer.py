from textual.app import App, ComposeResult
from textual.widgets import Header, Footer, SelectionList, Button, Label, LoadingIndicator, Static
from textual.containers import Container, Horizontal, Vertical
from textual.screen import Screen
from textual.worker import Worker
from textual import work
from rich.text import Text
import sh
import os
import subprocess
from pathlib import Path
from archclean.utils import run_command
from rich.filesize import decimal

class ResultScreen(Screen):
    BINDINGS = [("escape", "dismiss", "Close")]
    
    def __init__(self, count, size, failed):
        super().__init__()
        self.count = count
        self.reclaimed_size = size
        self.failed = failed

    def compose(self) -> ComposeResult:
        yield Container(
            Label("Deletion Complete", classes="title"),
            Label(f"Files Deleted: {self.count}"),
            Label(f"Space Reclaimed: {decimal(self.reclaimed_size)}"),
            Label(f"Failed: {self.failed}") if self.failed > 0 else Label(""),
            Button("OK", variant="primary", id="btn-ok"),
            classes="modal"
        )
    
    def on_button_pressed(self, event: Button.Pressed) -> None:
        self.dismiss()

class LargeFilesApp(App):
    CSS = """
    Screen {
        layout: vertical;
    }
    #legend {
        dock: top;
        height: auto;
        padding: 1;
        background: $boost;
        text-align: center;
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
    
    /* Modal CSS */
    .modal {
        background: $surface;
        padding: 2;
        border: thick $primary;
        width: 60;
        height: auto;
        align: center middle;
        text-align: center;
    }
    .title {
        text-style: bold;
        padding-bottom: 1;
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
        
        # Session Stats
        self.total_deleted_count = 0
        self.total_reclaimed_space = 0

    def compose(self) -> ComposeResult:
        yield Header()
        yield Static("Legend: [bold green]User Data[/] (Safe) | [bold yellow]Cache/Logs[/] (Review) | [bold red]System Files[/] (Caution)", id="legend")
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
                path_obj = Path(path)
                
                # Determine category and style
                str_path = str(path)
                if str_path.startswith("/home"):
                    style_color = "green"
                    category = "User"
                elif str_path.startswith(("/var/cache", "/tmp", "/var/tmp", "/var/log", "/root/.cache")):
                    style_color = "yellow"
                    category = "Cache"
                else:
                    style_color = "red"
                    category = "System"
                
                # Build Rich Text Label
                # Format: SIZE  [CATEGORY]  /path/to/ FILE
                text = Text()
                text.append(f"{human_size:>10} ", style="bold white")
                text.append(f"[{category:^6}] ", style=f"bold {style_color}")
                
                # Path formatting: dim directory, bold filename
                parent = str(path_obj.parent)
                if parent == ".": parent = ""
                else: parent += "/"
                
                text.append(parent, style=f"dim {style_color}")
                text.append(path_obj.name, style=f"bold {style_color}")
                
                # Use path as the value
                items.append((text, path))
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
        reclaimed_size = 0
        
        for path in selected:
            file_size = self.files_map.get(path, 0)
            try:
                # Remove file
                success = False
                if self.sudo:
                    if run_command("rm", ["-f", path], sudo=True):
                        success = True
                else:
                    os.remove(path)
                    success = True
                
                if success:
                    count += 1
                    reclaimed_size += file_size
            except Exception:
                # Try sudo if failed?
                if not self.sudo:
                     if run_command("rm", ["-f", path], sudo=True):
                         count += 1
                         reclaimed_size += file_size
                     else:
                         failed += 1
                else:
                    failed += 1
        
        self.total_deleted_count += count
        self.total_reclaimed_space += reclaimed_size
        
        self.query_one("#status", Label).update(f"Deleted {count} files. {failed} failed.")
        
        # Show Result Screen
        self.push_screen(ResultScreen(count, reclaimed_size, failed))
        
        # Refresh list
        self.scan_files()
