import click
from rich.console import Console
from archclean.cleaners import system, home, languages
from archclean.analyzer import analyze_disk_usage
from archclean.tracker import tracker

console = Console()

@click.group()
@click.option('--force', is_flag=True, help="Force actions without confirmation (use with caution).")
@click.pass_context
def cli(ctx, force):
    """ArchClean: A CLI tool for cleaning Arch Linux safely."""
    ctx.ensure_object(dict)
    ctx.obj['FORCE'] = force

@cli.command()
@click.pass_context
def full(ctx):
    """Runs the full interactive cleaning wizard."""
    force = ctx.obj['FORCE']
    console.print("[bold green]Starting ArchClean Wizard...[/bold green]")
    
    console.rule("[bold]System Cleaning[/bold]")
    system.clean_pacman_cache(force)
    system.clean_aur_helper_cache(force)
    system.remove_orphans(force)
    system.vacuum_journal(force)
    
    console.rule("[bold]Home Directory Cleaning[/bold]")
    home.clean_home(force)
    
    console.rule("[bold]Language & Runtime Caches[/bold]")
    languages.clean_language_caches(force)
    
    console.rule("[bold]Disk Analysis[/bold]")
    analyze_disk_usage(force)
    
    console.print("[bold green]ArchClean Finished![/bold green]")
    tracker.print_summary()

@cli.command()
@click.pass_context
def system_clean(ctx):
    """Performs only system-level cleaning."""
    force = ctx.obj['FORCE']
    system.clean_pacman_cache(force)
    system.clean_aur_helper_cache(force)
    system.remove_orphans(force)
    system.vacuum_journal(force)
    tracker.print_summary()

@cli.command()
@click.pass_context
def home_clean(ctx):
    """Performs only home directory cleaning."""
    force = ctx.obj['FORCE']
    home.clean_home(force)
    tracker.print_summary()

@cli.command()
@click.pass_context
def lang_clean(ctx):
    """Performs only language cache cleaning."""
    force = ctx.obj['FORCE']
    languages.clean_language_caches(force)
    tracker.print_summary()

@cli.command()
@click.pass_context
def analyze(ctx):
    """Runs disk usage analysis."""
    force = ctx.obj['FORCE']
    analyze_disk_usage(force)

if __name__ == '__main__':
    cli()