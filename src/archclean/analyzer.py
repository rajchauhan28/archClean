import sh
import os
from rich.console import Console
from archclean.utils import run_command, confirm_action, check_binary
from archclean.tui_analyzer import LargeFilesApp

console = Console()

def analyze_disk_usage(force=False):
    console.print("[bold cyan]Disk Usage Analyzer[/bold cyan]")
    
    choice = "1"
    if not force:
        console.print("1. Interactive Large File Cleaner (Built-in TUI)")
        console.print("2. ncdu (Standard CLI Tool)")
        from rich.prompt import Prompt
        choice = Prompt.ask("Choose an analyzer", choices=["1", "2"], default="1")

    target = os.path.expanduser("~")
    use_root = False
    
    # Check if user wants to analyze root
    if confirm_action("Do you want to analyze the ROOT directory (/) instead of HOME (~)?", force):
        target = "/"
        use_root = True

    if choice == "1":
        # Interactive TUI
        if use_root:
            # Refresh sudo credentials before starting TUI to avoid password prompt issues inside TUI
            run_command("sudo", ["-v"])
            
        app = LargeFilesApp(target_path=target, sudo=use_root)
        app.run()
        
        # Print CLI Summary after TUI exit
        if app.total_deleted_count > 0:
            from rich.filesize import decimal
            console.print("\n[bold green]Cleanup Summary:[/bold green]")
            console.print(f"  Files Deleted: {app.total_deleted_count}")
            console.print(f"  Space Reclaimed: {decimal(app.total_reclaimed_space)}")
    else:
        # ncdu fallback
        if not check_binary("ncdu"):
            console.print("[yellow]ncdu is not installed.[/yellow]")
            if confirm_action("Do you want to install ncdu? (sudo pacman -S ncdu)", force=False):
                run_command("pacman", ["-S", "ncdu"], sudo=True)
                if not check_binary("ncdu"):
                     console.print("[red]Failed to install ncdu.[/red]")
                     return
            else:
                 return

        args = [target]
        if use_root:
            args.append("-x")
        
        run_command("ncdu", args, sudo=use_root)