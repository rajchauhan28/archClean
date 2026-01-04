import sh
import os
from rich.console import Console
from archclean.utils import run_command, confirm_action, check_binary

console = Console()

def analyze_disk_usage(force=False):
    if not check_binary("ncdu"):
        console.print("[yellow]ncdu is not installed. It is recommended for analyzing disk usage.[/yellow]")
        if confirm_action("Do you want to install ncdu? (sudo pacman -S ncdu)", force=False):
            run_command("pacman", ["-S", "ncdu"], sudo=True)
            if not check_binary("ncdu"):
                 console.print("[red]Failed to install ncdu or not found after install.[/red]")
                 return
        else:
             console.print("[dim]Skipping disk analysis.[/dim]")
             return

    target = None
    if confirm_action("Do you want to analyze the HOME directory (~)?", force):
        target = os.path.expanduser("~")
        run_command("ncdu", [target])
    
    if confirm_action("Do you want to analyze the ROOT directory (/)? (Requires sudo)", force):
        target = "/"
        # -x: one file system (avoids /proc, /sys, /mnt loops)
        run_command("ncdu", [target, "-x"], sudo=True)