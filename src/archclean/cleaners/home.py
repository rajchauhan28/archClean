import os
import shutil
from pathlib import Path
from rich.console import Console
from archclean.utils import confirm_action
from archclean.tracker import tracker

console = Console()

def get_home_dir():
    return Path.home()

def clean_thumbnails(force=False):
    thumb_dir = get_home_dir() / ".cache" / "thumbnails"
    if thumb_dir.exists():
        size = 0
        for p in thumb_dir.rglob('*'):
            if p.is_file():
                size += p.stat().st_size
        
        size_mb = size / (1024 * 1024)
        if confirm_action(f"[bold yellow]Do you want to clean the thumbnail cache ({size_mb:.2f} MB)?[/bold yellow]", force):
            console.print("[blue]Cleaning thumbnails...[/blue]")
            try:
                shutil.rmtree(thumb_dir)
                console.print("[green]Thumbnails cleaned.[/green]")
                tracker.add("Home", "Thumbnails", "Cleaned", f"Freed {size_mb:.2f} MB")
            except Exception as e:
                console.print(f"[red]Error cleaning thumbnails: {e}[/red]")
                tracker.add("Home", "Thumbnails", "Failed", str(e))
        else:
            tracker.add("Home", "Thumbnails", "Skipped", f"{size_mb:.2f} MB kept")
    else:
        tracker.add("Home", "Thumbnails", "Cleaned", "Already empty")

def empty_trash(force=False):
    trash_dir = get_home_dir() / ".local" / "share" / "Trash"
    if trash_dir.exists():
        files = list(trash_dir.rglob('*'))
        if not files:
            console.print("[dim]Trash is empty.[/dim]")
            tracker.add("Home", "Trash", "Cleaned", "Already empty")
            return

        if confirm_action("[bold yellow]Do you want to empty the Trash?[/bold yellow]", force):
            console.print("[blue]Emptying Trash...[/blue]")
            try:
                for item in trash_dir.iterdir():
                    if item.is_dir():
                        shutil.rmtree(item)
                    else:
                        item.unlink()
                console.print("[green]Trash emptied.[/green]")
                tracker.add("Home", "Trash", "Cleaned", "Trash emptied")
            except Exception as e:
                console.print(f"[red]Error emptying Trash: {e}[/red]")
                tracker.add("Home", "Trash", "Failed", str(e))
        else:
            tracker.add("Home", "Trash", "Skipped", "Items kept")
    else:
        tracker.add("Home", "Trash", "Not Found", "Directory missing")

def clean_home(force=False):
    clean_thumbnails(force)
    empty_trash(force)