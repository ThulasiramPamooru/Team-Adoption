from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich import box

console = Console()

PHASE_ICONS = {
    "ANALYSIS": "🔍",
    "DOCUMENTED": "📄",
    "SECURITY": "🔒",
    "TESTED": "🧪",
    "COMMITTED": "💾",
    "PR_CREATED": "🔀",
    "DEPLOYED": "🚀",
}

STATUS_COLORS = {
    "PENDING": "dim",
    "IN_PROGRESS": "blue",
    "PASSED": "green",
    "FAILED": "red",
    "BLOCKED": "yellow",
    "SKIPPED": "dim",
    "COMPLETED": "green",
    "RUNNING": "blue",
    "AWAITING_APPROVAL": "yellow",
}


def print_workflow_table(workflows: list[dict]):
    table = Table(title="FlowGuard Workflow Runs", box=box.ROUNDED)
    table.add_column("Task ID", style="cyan bold")
    table.add_column("Title", max_width=40)
    table.add_column("App")
    table.add_column("Status")
    table.add_column("Phase")
    table.add_column("Updated")

    for wf in workflows:
        status = wf.get("status", "")
        color = STATUS_COLORS.get(status, "white")
        table.add_row(
            wf.get("task_id", ""),
            wf.get("title", "")[:40],
            wf.get("target_app", ""),
            f"[{color}]{status}[/{color}]",
            wf.get("current_phase") or "—",
            wf.get("updated_at", "")[:16],
        )
    console.print(table)


def print_workflow_detail(wf: dict):
    console.print(Panel(
        f"[bold cyan]{wf.get('task_id')}[/] — {wf.get('title')}\n"
        f"App: [bold]{wf.get('target_app')}[/] | Status: {wf.get('status')}",
        title="FlowGuard Workflow",
        border_style="blue",
    ))

    steps = wf.get("steps", [])
    table = Table(box=box.SIMPLE)
    table.add_column("#")
    table.add_column("Phase")
    table.add_column("Status")
    table.add_column("Duration")

    phases = ["ANALYSIS", "DOCUMENTED", "SECURITY", "TESTED", "COMMITTED", "PR_CREATED", "DEPLOYED"]
    step_map = {s["phase"]: s for s in steps}

    for i, phase in enumerate(phases, 1):
        step = step_map.get(phase)
        status = step.get("status", "PENDING") if step else "PENDING"
        color = STATUS_COLORS.get(status, "white")
        duration = ""
        if step and step.get("duration_ms"):
            ms = step["duration_ms"]
            duration = f"{ms}ms" if ms < 1000 else f"{ms/1000:.1f}s"

        table.add_row(
            str(i),
            f"{PHASE_ICONS.get(phase, '')} {phase}",
            f"[{color}]{status}[/{color}]",
            duration,
        )

    console.print(table)

    if wf.get("github_pr_url"):
        console.print(f"\n🔀 PR: {wf['github_pr_url']}")
    if wf.get("jira_url"):
        console.print(f"📋 Jira: {wf['jira_url']}")
