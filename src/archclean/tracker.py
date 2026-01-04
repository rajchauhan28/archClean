from rich.table import Table
from rich.console import Console

console = Console()

class Tracker:
    def __init__(self):
        self.records = []

    def add(self, category, action, status, info=""):
        self.records.append({
            "Category": category,
            "Action": action,
            "Status": status,
            "Info": info
        })

    def print_summary(self):
        if not self.records:
            return

        table = Table(title="ArchClean Report")
        table.add_column("Category", style="cyan", no_wrap=True)
        table.add_column("Action", style="magenta")
        table.add_column("Status", style="green")
        table.add_column("Details", style="yellow")

        for r in self.records:
            status_style = "green"
            if r["Status"] in ["Skipped", "Not Found"]:
                status_style = "dim"
            elif r["Status"] == "Failed":
                status_style = "bold red"
            
            table.add_row(
                r["Category"], 
                r["Action"], 
                f"[{status_style}]{r['Status']}[/{status_style}]", 
                r["Info"]
            )

        console.print("\n")
        console.print(table)

tracker = Tracker()