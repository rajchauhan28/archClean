import sh
import click
import re
from rich.console import Console
from rich.prompt import Confirm
from archclean.utils import run_command, confirm_action, check_binary
from archclean.tracker import tracker

console = Console()

def clean_pacman_cache(force=False):
    try:
        cache_dirs = sh.Command("pacman-conf")("CacheDir").strip().split('\n')
    except (sh.ErrorReturnCode, sh.CommandNotFound):
        cache_dirs = ["/var/cache/pacman/pkg/"]

    found_broken = []
    from pathlib import Path
    
    for cdir in cache_dirs:
        p = Path(cdir.strip())
        if p.exists() and p.is_dir():
            try:
                for item in p.iterdir():
                    if item.is_dir():
                        found_broken.append(item)
            except PermissionError:
                pass
    
    if found_broken:
        console.print(f"[bold red]Found {len(found_broken)} broken/partial download directories in Pacman cache.[/bold red]")
        if confirm_action("[bold yellow]Do you want to remove these broken artifacts first? (Fixes 'Is a directory' errors)[/bold yellow]", force):
            console.print("[blue]Removing broken artifacts...[/blue]")
            success_count = 0
            for broken in found_broken:
                if run_command("rm", ["-rf", str(broken)], sudo=True):
                    success_count += 1
            tracker.add("System", "Broken Downloads", "Cleaned", f"Removed {success_count} dirs")
        else:
            tracker.add("System", "Broken Downloads", "Skipped", "User declined")

    thorough = False
    if not force:
        thorough = Confirm.ask("[bold yellow]Do you want to perform a thorough Pacman cache clean? (pacman -Scc removes all cached packages)[/bold yellow]", default=False)
    
    cmd_flag = "-Scc" if thorough else "-Sc"
    action_name = f"Pacman Cache ({cmd_flag})"

    if force or confirm_action(f"[bold yellow]Do you want to clean the Pacman cache? (pacman {cmd_flag})[/bold yellow]", force):
        console.print(f"[blue]Cleaning Pacman cache with {cmd_flag}...[/blue]")
        args = [cmd_flag]
        if force:
             args.append("--noconfirm")
        if run_command("pacman", args, sudo=True):
            tracker.add("System", action_name, "Cleaned", "Cache cleared")
        else:
            tracker.add("System", action_name, "Failed", "Check logs")
    else:
        tracker.add("System", action_name, "Skipped", "User declined")

def clean_aur_helper_cache(force=False):
    helper = None
    if check_binary("paru"):
        helper = "paru"
    elif check_binary("yay"):
        helper = "yay"
    
    if helper:
        if confirm_action(f"[bold yellow]Do you want to clean the {helper} cache? ({helper} -Sc)[/bold yellow]", force):
            console.print(f"[blue]Cleaning {helper} cache...[/blue]")
            args = ["-Sc"]
            if force:
                args.append("--noconfirm")
            if run_command(helper, args, sudo=False):
                tracker.add("System", f"AUR Helper ({helper})", "Cleaned", "Cache cleared")
            else:
                tracker.add("System", f"AUR Helper ({helper})", "Failed", "Check logs")
        else:
            tracker.add("System", f"AUR Helper ({helper})", "Skipped", "User declined")
    else:
        tracker.add("System", "AUR Helper", "Not Found", "Neither yay nor paru found")

def remove_orphans(force=False):
    try:
        orphans = sh.pacman("-Qtdq", "--color=never", _ok_code=[0, 1])
    except sh.ErrorReturnCode:
        orphans = ""

    if not orphans.strip():
        console.print("[green]No orphan packages found.[/green]")
        tracker.add("System", "Orphans", "Cleaned", "No orphans found")
        return

    ansi_escape = re.compile(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])')
    orphan_list = [ansi_escape.sub('', pkg).strip() for pkg in orphans.strip().split('\n') if ansi_escape.sub('', pkg).strip()]

    count = len(orphan_list)
    if count == 0:
        console.print("[green]No orphan packages found.[/green]")
        tracker.add("System", "Orphans", "Cleaned", "No orphans found")
        return

    console.print(f"[bold magenta]Found {count} orphan packages:[/bold magenta] {', '.join(orphan_list)}")

    if confirm_action("[bold yellow]Do you want to remove these orphans?[/bold yellow]", force):
        console.print("[blue]Removing orphans...[/blue]")
        args = ["-Rns"] + orphan_list
        if force:
            args.append("--noconfirm")
        if run_command("pacman", args, sudo=True):
            tracker.add("System", "Orphans", "Cleaned", f"Removed {count} packages")
        else:
            tracker.add("System", "Orphans", "Failed", "Removal failed")
    else:
        tracker.add("System", "Orphans", "Skipped", f"{count} orphans kept")

def vacuum_journal(force=False):
    if confirm_action("[bold yellow]Do you want to vacuum system journals to 2 weeks? (journalctl --vacuum-time=2weeks)[/bold yellow]", force):
        console.print("[blue]Vacuuming journals...[/blue]")
        if run_command("journalctl", ["--vacuum-time=2weeks"], sudo=True):
            tracker.add("System", "Journal", "Cleaned", "Vacuumed to 2 weeks")
        else:
            tracker.add("System", "Journal", "Failed", "Command failed")
    else:
        tracker.add("System", "Journal", "Skipped", "User declined")