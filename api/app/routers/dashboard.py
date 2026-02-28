from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from pydantic import BaseModel

from app.core.database import get_db
from app.core.auth import get_current_user
from app.models.workflow import Workflow

router = APIRouter(prefix="/dashboard", tags=["dashboard"])


class DashboardStats(BaseModel):
    total_runs: int
    completed: int
    failed: int
    blocked: int
    running: int
    success_rate: float


@router.get("/stats", response_model=DashboardStats)
async def get_stats(
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    result = await db.execute(
        select(Workflow.status, func.count().label("count"))
        .group_by(Workflow.status)
    )
    rows = result.all()
    counts = {row.status: row.count for row in rows}
    total = sum(counts.values())
    completed = counts.get("COMPLETED", 0)
    success_rate = round((completed / total * 100), 1) if total > 0 else 0.0

    return DashboardStats(
        total_runs=total,
        completed=completed,
        failed=counts.get("FAILED", 0),
        blocked=counts.get("BLOCKED", 0) + counts.get("AWAITING_APPROVAL", 0),
        running=counts.get("RUNNING", 0),
        success_rate=success_rate,
    )
