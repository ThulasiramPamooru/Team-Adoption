import typer
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich import box
from flowguard.utils.api_client import get

console = Console()


def report_command(
    task_id: str = typer.Argument(..., help="Jira task ID (e.g. DIPA-123)"),
):
    """Display the Playwright test report summary for a task."""
    try:
        # Find workflow
        data = get("/workflows", params={"page": 1, "per_page": 50})
        workflows = data.get("items", [])
        wf = next(
            (w for w in workflows if w["task_id"].upper() == task_id.upper()),
            None,
        )
        if not wf:
            console.print(f"[yellow]No workflow found for {task_id}[/]")
            raise typer.Exit(1)

        # Fetch test report
        report = get(f"/reports/test/{wf['id']}")
        passed = report["passed"]
        failed = report["failed"]
        total = report["total"]
        status_color = "green" if failed == 0 else "red"
        status_icon = "✅" if failed == 0 else "❌"

        console.print(Panel(
            f"{status_icon} [bold {status_color}]{passed}/{total} tests passed[/]"
            + (f"\n[red]{failed} failed[/]" if failed else ""),
            title=f"Test Report — {task_id}",
            border_style=status_color,
        ))

        console.print(f"\n[bold]Commit Message:[/]")
        console.print(report.get("commit_message", "—"))

        if report.get("html_path"):
            import os
            url = os.getenv("API_URL", "http://localhost:8000")
            console.print(f"\n[blue]HTML Report:[/] {url}/api/v1/reports/file/{report['id']}")

    except typer.Exit:
        raise
    except Exception as e:
        console.print(f"[red]Error fetching report: {e}[/]")
        raise typer.Exit(1)
