import click
import sh
import sys
import os
import shutil
from rich.console import Console
from rich.prompt import Confirm

console = Console()

def run_command(command, args, sudo=False, shell=False, capture=False, cwd=None):
    """Runs a command, optionally with sudo, capturing output or running in foreground."""
    if sudo and os.geteuid() != 0:
        cmd_func = sh.sudo.bake(command)
    else:
        try:
            cmd_func = getattr(sh, command)
        except AttributeError:
            console.print(f"[bold red]Error:[/bold red] Command '{command}' not found.")
            return None if capture else False

    try:
        kwargs = {}
        if cwd:
            kwargs['_cwd'] = cwd
        
        if capture:
            result = cmd_func(*args, **kwargs)
            return result.stdout.decode('utf-8')
        else:
            cmd_func(*args, _fg=True, **kwargs)
            return True
    except sh.ErrorReturnCode as e:
        if not capture:
            console.print(f"[bold red]Error running {command}:[/bold red] {e}")
        return None if capture else False
    except Exception as e:
        if not capture:
            console.print(f"[bold red]Unexpected error:[/bold red] {e}")
        return None if capture else False

def confirm_action(message, force=False):
    if force:
        return True
    return Confirm.ask(message, default=False)

def check_binary(binary_name):
    return shutil.which(binary_name) is not None