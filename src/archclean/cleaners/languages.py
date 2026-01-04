from rich.console import Console
from archclean.utils import run_command, confirm_action, check_binary
from archclean.tracker import tracker

console = Console()

def clean_python_cache(force=False):
    if check_binary("python") or check_binary("python3"):
        if check_binary("pip"):
            if confirm_action("[bold yellow]Do you want to clean the pip cache? (pip cache purge)[/bold yellow]", force):
                console.print("[blue]Cleaning pip cache...[/blue]")
                if run_command("pip", ["cache", "purge"]):
                    tracker.add("Language", "Python (pip)", "Cleaned", "Cache purged")
                else:
                    tracker.add("Language", "Python (pip)", "Failed", "Command failed")
            else:
                tracker.add("Language", "Python (pip)", "Skipped", "User declined")

def clean_node_cache(force=False):
    if check_binary("node"):
        if check_binary("npm"):
            if confirm_action("[bold yellow]Do you want to clean the npm cache? (npm cache clean --force)[/bold yellow]", force):
                console.print("[blue]Cleaning npm cache...[/blue]")
                if run_command("npm", ["cache", "clean", "--force"]):
                    tracker.add("Language", "Node (npm)", "Cleaned", "Cache cleaned")
                else:
                    tracker.add("Language", "Node (npm)", "Failed", "Command failed")
            else:
                tracker.add("Language", "Node (npm)", "Skipped", "User declined")
        
        if check_binary("yarn"):
            if confirm_action("[bold yellow]Do you want to clean the yarn cache? (yarn cache clean)[/bold yellow]", force):
                 console.print("[blue]Cleaning yarn cache...[/blue]")
                 if run_command("yarn", ["cache", "clean"]):
                     tracker.add("Language", "Node (yarn)", "Cleaned", "Cache cleaned")
                 else:
                     tracker.add("Language", "Node (yarn)", "Failed", "Command failed")
            else:
                tracker.add("Language", "Node (yarn)", "Skipped", "User declined")

def clean_rust_cache(force=False):
    if check_binary("rustc") or check_binary("cargo"):
        if check_binary("cargo-cache"):
            if confirm_action("[bold yellow]Do you want to clean the Cargo cache using cargo-cache?[/bold yellow]", force):
                console.print("[blue]Cleaning Cargo cache...[/blue]")
                if run_command("cargo-cache", ["--remove-dir", "all"]):
                    tracker.add("Language", "Rust (cargo-cache)", "Cleaned", "All caches removed")
                else:
                    tracker.add("Language", "Rust (cargo-cache)", "Failed", "Command failed")
            else:
                tracker.add("Language", "Rust (cargo-cache)", "Skipped", "User declined")
        else:
            if confirm_action("[bold yellow]Do you want to manually clear Cargo registry & index caches? (~/.cargo/registry and ~/.cargo/git)[/bold yellow]", force):
                console.print("[blue]Clearing Cargo caches...[/blue]")
                import shutil
                from pathlib import Path
                cargo_home = Path.home() / ".cargo"
                success = True
                for folder in ["registry", "git"]:
                    target = cargo_home / folder
                    if target.exists():
                        try:
                            shutil.rmtree(target)
                            console.print(f"[green]Cleared {target}[/green]")
                        except Exception as e:
                            console.print(f"[red]Error clearing {target}: {e}[/red]")
                            success = False
                
                if success:
                    tracker.add("Language", "Rust (Manual)", "Cleaned", "Registry/Git cleared")
                else:
                    tracker.add("Language", "Rust (Manual)", "Failed", "Some errors occurred")
            else:
                tracker.add("Language", "Rust", "Skipped", "User declined")

def clean_go_cache(force=False):
    if check_binary("go"):
        if confirm_action("[bold yellow]Do you want to clean the go module cache? (go clean -modcache)[/bold yellow]", force):
            console.print("[blue]Cleaning go module cache...[/blue]")
            if run_command("go", ["clean", "-modcache"]):
                tracker.add("Language", "Go", "Cleaned", "Module cache cleared")
            else:
                tracker.add("Language", "Go", "Failed", "Command failed")
        else:
            tracker.add("Language", "Go", "Skipped", "User declined")

def clean_php_cache(force=False):
    if check_binary("php"):
        if check_binary("composer"):
            if confirm_action("[bold yellow]Do you want to clean the Composer cache? (composer clear-cache)[/bold yellow]", force):
                console.print("[blue]Cleaning Composer cache...[/blue]")
                if run_command("composer", ["clear-cache"]):
                    tracker.add("Language", "PHP (Composer)", "Cleaned", "Cache cleared")
                else:
                    tracker.add("Language", "PHP (Composer)", "Failed", "Command failed")
            else:
                tracker.add("Language", "PHP (Composer)", "Skipped", "User declined")

def clean_ruby_cache(force=False):
    if check_binary("ruby"):
        if check_binary("gem"):
            if confirm_action("[bold yellow]Do you want to clean old Ruby gems? (gem cleanup)[/bold yellow]", force):
                console.print("[blue]Cleaning Ruby gems...[/blue]")
                if run_command("gem", ["cleanup"]):
                    tracker.add("Language", "Ruby (Gems)", "Cleaned", "Cleanup run")
                else:
                    tracker.add("Language", "Ruby (Gems)", "Failed", "Command failed")
            else:
                tracker.add("Language", "Ruby (Gems)", "Skipped", "User declined")

def clean_java_cache(force=False):
    if check_binary("java"):
        if check_binary("gradle"):
            if confirm_action("[bold yellow]Do you want to clean the global Gradle cache? (~/.gradle/caches)[/bold yellow]", force):
                console.print("[blue]Cleaning Gradle cache...[/blue]")
                import shutil
                from pathlib import Path
                gradle_cache = Path.home() / ".gradle" / "caches"
                if gradle_cache.exists():
                     try:
                        run_command("rm", ["-rf", str(gradle_cache)])
                        console.print("[green]Gradle cache cleaned.[/green]")
                        tracker.add("Language", "Java (Gradle)", "Cleaned", "Caches removed")
                     except Exception as e:
                        console.print(f"[red]Error cleaning Gradle cache: {e}[/red]")
                        tracker.add("Language", "Java (Gradle)", "Failed", str(e))
                else:
                    tracker.add("Language", "Java (Gradle)", "Cleaned", "Already empty")
            else:
                tracker.add("Language", "Java (Gradle)", "Skipped", "User declined")

def clean_bun_cache(force=False):
    if check_binary("bun"):
        if confirm_action("[bold yellow]Do you want to clean the Bun cache? (~/.bun/install/cache)[/bold yellow]", force):
            console.print("[blue]Cleaning Bun cache...[/blue]")
            import shutil
            from pathlib import Path
            bun_cache = Path.home() / ".bun" / "install" / "cache"
            if bun_cache.exists():
                try:
                    shutil.rmtree(bun_cache)
                    console.print("[green]Bun cache cleaned.[/green]")
                    tracker.add("Language", "Bun", "Cleaned", "Cache directory removed")
                except Exception as e:
                    console.print(f"[red]Error cleaning Bun cache: {e}[/red]")
                    tracker.add("Language", "Bun", "Failed", str(e))
            else:
                 tracker.add("Language", "Bun", "Cleaned", "Already empty")
        else:
            tracker.add("Language", "Bun", "Skipped", "User declined")

def clean_docker_cache(force=False):
    if check_binary("docker"):
        if confirm_action("[bold yellow]Do you want to prune Docker system (containers, networks, images)? (docker system prune)[/bold yellow]", force):
            console.print("[blue]Pruning Docker system...[/blue]")
            args = ["system", "prune"]
            if force:
                args.append("--force")
            
            if run_command("docker", args):
                tracker.add("System", "Docker", "Cleaned", "System pruned")
            else:
                tracker.add("System", "Docker", "Failed", "Command failed")
        else:
             tracker.add("System", "Docker", "Skipped", "User declined")

def clean_ccache(force=False):
    if check_binary("ccache"):
        if confirm_action("[bold yellow]Do you want to clear the C/C++ compiler cache? (ccache -C)[/bold yellow]", force):
            console.print("[blue]Clearing ccache...[/blue]")
            if run_command("ccache", ["-C"]):
                tracker.add("Language", "C/C++ (ccache)", "Cleaned", "Cache cleared")
            else:
                tracker.add("Language", "C/C++ (ccache)", "Failed", "Command failed")
        else:
            tracker.add("Language", "C/C++ (ccache)", "Skipped", "User declined")

def clean_dotnet_cache(force=False):
    if check_binary("dotnet"):
        if confirm_action("[bold yellow]Do you want to clean local NuGet resources? (dotnet nuget locals all --clear)[/bold yellow]", force):
            console.print("[blue]Cleaning NuGet cache...[/blue]")
            if run_command("dotnet", ["nuget", "locals", "all", "--clear"]):
                 tracker.add("Language", ".NET (NuGet)", "Cleaned", "Locals cleared")
            else:
                 tracker.add("Language", ".NET (NuGet)", "Failed", "Command failed")
        else:
            tracker.add("Language", ".NET (NuGet)", "Skipped", "User declined")

def clean_cpp_cache(force=False):
    if check_binary("gcc") or check_binary("clang") or check_binary("cc"):
        clean_ccache(force)

def clean_language_caches(force=False):
    clean_python_cache(force)
    clean_node_cache(force)
    clean_bun_cache(force)
    clean_rust_cache(force)
    clean_go_cache(force)
    clean_php_cache(force)
    clean_ruby_cache(force)
    clean_java_cache(force)
    clean_dotnet_cache(force)
    clean_cpp_cache(force)
    clean_docker_cache(force)