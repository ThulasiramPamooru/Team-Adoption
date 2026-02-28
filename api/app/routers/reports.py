from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import FileResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, desc
from pydantic import BaseModel
from typing import Optional
from datetime import datetime
import os

from app.core.database import get_db
from app.core.auth import get_current_user
from app.models.workflow import TestReport, SecurityReport
from app.core.config import get_settings

router = APIRouter(prefix="/reports", tags=["reports"])
settings = get_settings()


class TestReportOut(BaseModel):
    id: str
    workflow_id: str
    task_id: str
    passed: int
    failed: int
    skipped: int
    total: int
    duration_ms: int
    html_path: Optional[str]
    json_path: Optional[str]
    summary: str
    commit_message: str
    created_at: datetime

    class Config:
        from_attributes = True


class PaginatedReports(BaseModel):
    items: list[TestReportOut]
    total: int
    page: int
    per_page: int
    pages: int


@router.get("", response_model=PaginatedReports)
async def list_reports(
    page: int = 1,
    per_page: int = 20,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    offset = (page - 1) * per_page
    count_q = await db.execute(select(func.count()).select_from(TestReport))
    total = count_q.scalar_one()

    result = await db.execute(
        select(TestReport).order_by(desc(TestReport.created_at)).offset(offset).limit(per_page)
    )
    reports = result.scalars().all()

    return PaginatedReports(
        items=list(reports),
        total=total,
        page=page,
        per_page=per_page,
        pages=(total + per_page - 1) // per_page,
    )


@router.get("/test/{workflow_id}", response_model=TestReportOut)
async def get_test_report(
    workflow_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    result = await db.execute(
        select(TestReport).where(TestReport.workflow_id == workflow_id)
    )
    report = result.scalar_one_or_none()
    if not report:
        raise HTTPException(status_code=404, detail="Test report not found")
    return report


@router.get("/file/{report_id}")
async def serve_html_report(
    report_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    result = await db.execute(select(TestReport).where(TestReport.id == report_id))
    report = result.scalar_one_or_none()
    if not report or not report.html_path:
        raise HTTPException(status_code=404, detail="Report file not found")

    file_path = os.path.join(settings.test_reports_path, report.html_path)
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="Report file missing on disk")

    return FileResponse(file_path, media_type="text/html")
