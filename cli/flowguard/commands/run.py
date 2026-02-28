import typer
from rich.console import Console
from rich.panel import Panel
from flowguard.utils.api_client import post
from flowguard.utils.display import print_workflow_detail

console = Console()


def run_command(
    task_id: str = typer.Argument(..., help="Jira task ID (e.g. DIPA-123)"),
    app: str = typer.Option(..., "--app", "-a", help="Target application name"),
    title: str = typer.Option("", "--title", "-t", help="Short title for this workflow run"),
    description: str = typer.Option("", "--description", "-d", help="Optional description"),
):
    """Trigger a full 7-phase FlowGuard workflow for a JIRA task."""
    if not task_id.startswith("DIPA-"):
        task_id = f"DIPA-{task_id}"

    if not title:
        title = typer.prompt("Workflow title")

    console.print(Panel(
        f"[bold cyan]{task_id}[/] → [bold]{app}[/]\n{title}",
        title="[bold blue]🛡 FlowGuard — Starting Workflow[/]",
        border_style="blue",
    ))

    try:
        workflow = post("/workflows", json={
            "task_id": task_id,
            "target_app": app,
            "title": title,
            "description": description or None,
        })
        console.print(f"\n[green]✓[/] Workflow started: [bold]{workflow['id']}[/]")
        console.print(f"  7 phases queued. Monitor at: [blue]flowguard status {task_id}[/]")
        console.print(f"  Dashboard: [blue]{_get_web_url()}/workflows/{workflow['id']}[/]")

    except Exception as e:
        console.print(f"[red]Error starting workflow: {e}[/]")
        raise typer.Exit(1)


def _get_web_url() -> str:
    import os
    return os.getenv("WEB_URL", "http://localhost:5173")
