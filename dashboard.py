import os
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

console = Console()

def showDashboard(query: str, tool: str, risk_score: float, severity: str, decision: str, reason: str):
    os.system("clear")
    console.print(
        Panel.fit(
            "[bold cyan]AEGIS - Runtime Firewall for AI Agents[/bold cyan]"
        )
    )

    table = Table(title="Security Assessment")

    table.add_column("Field", style="cyan")
    table.add_column("Value", style="white")

    table.add_row("Query", query)
    table.add_row("Tool", tool)
    table.add_row("Risk Score", str(risk_score))
    table.add_row("Severity", severity)
    table.add_row("Decision", decision)
    table.add_row("Reason", reason)

    console.print(table)