import typer
from rich.console import Console
from flowguard.utils.api_client import get
from flowguard.utils.display import print_workflow_detail, print_workflow_table

console = Console()


def status_command(
    task_id: str = typer.Argument(..., help="Jira task ID or workflow run ID"),
):
    """Show the current status of a workflow run."""
    try:
        # Try fetching by listing and filtering by task_id
        data = get("/workflows", params={"page": 1, "per_page": 50})
        workflows = data.get("items", [])
        matches = [
            wf for wf in workflows
            if wf["task_id"].upper() == task_id.upper()
            or wf["id"] == task_id
        ]

        if not matches:
            console.print(f"[yellow]No workflow found for {task_id}[/]")
            raise typer.Exit(1)

        wf = matches[0]  # Most recent
        print_workflow_detail(wf)

    except typer.Exit:
        raise
    except Exception as e:
        console.print(f"[red]Error fetching status: {e}[/]")
        raise typer.Exit(1)
