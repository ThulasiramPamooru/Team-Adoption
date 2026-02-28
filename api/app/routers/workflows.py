from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, desc
from sqlalchemy.orm import selectinload
from pydantic import BaseModel
from typing import Optional
import uuid
from datetime import datetime

from app.core.database import get_db
from app.core.auth import get_current_user
from app.models.workflow import Workflow, WorkflowStep
from app.services.workflow_engine import WorkflowEngine
from app.services.websocket_manager import manager

router = APIRouter(prefix="/workflows", tags=["workflows"])


# ── Pydantic schemas ──────────────────────────
class CreateWorkflowRequest(BaseModel):
    task_id: str
    target_app: str
    title: str
    description: Optional[str] = None


class WorkflowStepOut(BaseModel):
    id: str
    phase: str
    status: str
    output: Optional[str]
    duration_ms: Optional[int]
    artifacts: Optional[dict]
    started_at: Optional[datetime]
    completed_at: Optional[datetime]

    class Config:
        from_attributes = True


class WorkflowOut(BaseModel):
    id: str
    task_id: str
    target_app: str
    title: str
    description: Optional[str]
    status: str
    current_phase: Optional[str]
    steps: list[WorkflowStepOut]
    created_by: str
    created_at: datetime
    updated_at: datetime
    jira_url: Optional[str]
    github_pr_url: Optional[str]
    github_branch: Optional[str]
    test_report_path: Optional[str]

    class Config:
        from_attributes = True


class PaginatedWorkflows(BaseModel):
    items: list[WorkflowOut]
    total: int
    page: int
    per_page: int
    pages: int


# ── Routes ──────────────────────────────────
@router.get("", response_model=PaginatedWorkflows)
async def list_workflows(
    page: int = 1,
    per_page: int = 20,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    offset = (page - 1) * per_page
    count_q = await db.execute(select(func.count()).select_from(Workflow))
    total = count_q.scalar_one()

    result = await db.execute(
        select(Workflow)
        .options(selectinload(Workflow.steps))
        .order_by(desc(Workflow.created_at))
        .offset(offset)
        .limit(per_page)
    )
    workflows = result.scalars().unique().all()

    return PaginatedWorkflows(
        items=list(workflows),
        total=total,
        page=page,
        per_page=per_page,
        pages=(total + per_page - 1) // per_page,
    )


@router.post("", response_model=WorkflowOut, status_code=status.HTTP_201_CREATED)
async def create_workflow(
    body: CreateWorkflowRequest,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    workflow = Workflow(
        id=str(uuid.uuid4()),
        task_id=body.task_id.upper(),
        target_app=body.target_app,
        title=body.title,
        description=body.description,
        status="PENDING",
        created_by=current_user.get("sub", "unknown"),
    )
    db.add(workflow)
    await db.flush()

    # Pre-create all 7 phase steps as PENDING
    phases = ["ANALYSIS", "DOCUMENTED", "SECURITY", "TESTED", "COMMITTED", "PR_CREATED", "DEPLOYED"]
    for phase in phases:
        step = WorkflowStep(
            id=str(uuid.uuid4()),
            workflow_id=workflow.id,
            phase=phase,
            status="PENDING",
        )
        db.add(step)

    await db.commit()

    # Re-fetch with steps eagerly loaded (avoids MissingGreenlet on serialization)
    result = await db.execute(
        select(Workflow).options(selectinload(Workflow.steps)).where(Workflow.id == workflow.id)
    )
    workflow = result.scalar_one()

    # Kick off workflow in background
    engine = WorkflowEngine()
    background_tasks.add_task(engine.run, workflow.id)

    return workflow


@router.get("/{workflow_id}", response_model=WorkflowOut)
async def get_workflow(
    workflow_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    result = await db.execute(select(Workflow).options(selectinload(Workflow.steps)).where(Workflow.id == workflow_id))
    workflow = result.scalar_one_or_none()
    if not workflow:
        raise HTTPException(status_code=404, detail="Workflow not found")
    return workflow


@router.post("/{workflow_id}/approve", response_model=WorkflowOut)
async def approve_workflow_phase(
    workflow_id: str,
    body: dict,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """Admin approves a BLOCKED phase to continue."""
    roles = current_user.get("https://flowguard/roles", [])
    if "admin" not in roles:
        raise HTTPException(status_code=403, detail="Admin required to approve phases")

    result = await db.execute(select(Workflow).options(selectinload(Workflow.steps)).where(Workflow.id == workflow_id))
    workflow = result.scalar_one_or_none()
    if not workflow:
        raise HTTPException(status_code=404, detail="Workflow not found")

    workflow.status = "RUNNING"
    await db.commit()
    await db.refresh(workflow)

    engine = WorkflowEngine()
    background_tasks.add_task(engine.resume, workflow_id, body.get("phase"))

    return workflow


@router.post("/{workflow_id}/cancel", response_model=WorkflowOut)
async def cancel_workflow(
    workflow_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    result = await db.execute(select(Workflow).options(selectinload(Workflow.steps)).where(Workflow.id == workflow_id))
    workflow = result.scalar_one_or_none()
    if not workflow:
        raise HTTPException(status_code=404, detail="Workflow not found")
    workflow.status = "FAILED"
    await db.commit()
    await db.refresh(workflow)
    return workflow
