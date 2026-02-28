"""
FlowGuard CLI — Entry Point
Usage: flowguard <command> [options]
"""
import typer
from rich.console import Console
from rich import print as rprint

from flowguard.commands.run import run_command
from flowguard.commands.status import status_command
from flowguard.commands.report import report_command
from flowguard import __version__

app = typer.Typer(
    name="flowguard",
    help="🛡 FlowGuard — AI Engineering Delivery Platform\n\nSafe, tested, reviewed delivery in 7 phases.",
    no_args_is_help=True,
    add_completion=False,
)

console = Console()


@app.callback()
def callback():
    """FlowGuard CLI v{__version__}""".format(__version__=__version__)


@app.command("run")
def run(
    task_id: str = typer.Argument(..., help="Jira task ID, e.g. DIPA-123"),
    app: str = typer.Option(..., "--app", "-a", help="Target application"),
    title: str = typer.Option("", "--title", "-t", help="Short title"),
    description: str = typer.Option("", "--desc", "-d", help="Description"),
):
    """Trigger a full 7-phase FlowGuard workflow run."""
    run_command(task_id=task_id, app=app, title=title, description=description)


@app.command("status")
def status(
    task_id: str = typer.Argument(..., help="Jira task ID or workflow run ID"),
):
    """Show current phase status of a workflow run."""
    status_command(task_id=task_id)


@app.command("report")
def report(
    task_id: str = typer.Argument(..., help="Jira task ID"),
):
    """Show Playwright test report summary."""
    report_command(task_id=task_id)


@app.command("list")
def list_runs():
    """List all workflow runs."""
    from flowguard.utils.api_client import get
    from flowguard.utils.display import print_workflow_table
    try:
        data = get("/workflows", params={"page": 1, "per_page": 20})
        print_workflow_table(data.get("items", []))
    except Exception as e:
        console.print(f"[red]Error: {e}[/]")
        raise typer.Exit(1)


@app.command("version")
def version():
    """Show FlowGuard CLI version."""
    console.print(f"FlowGuard CLI v{__version__}")


if __name__ == "__main__":
    app()
