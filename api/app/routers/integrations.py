from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from pydantic import BaseModel
from typing import Optional
from datetime import datetime
import uuid
import base64

from app.core.database import get_db
from app.core.auth import get_current_user
from app.models.workflow import Integration

router = APIRouter(prefix="/integrations", tags=["integrations"])


def _encrypt(value: str) -> str:
    """Simple base64 encoding — use Fernet in production."""
    return base64.b64encode(value.encode()).decode()


def _decrypt(value: str) -> str:
    return base64.b64decode(value.encode()).decode()


class IntegrationOut(BaseModel):
    id: str
    provider: str
    connected: bool
    connected_at: Optional[datetime]

    class Config:
        from_attributes = True


class GithubTokenRequest(BaseModel):
    token: str


class JiraCredentialsRequest(BaseModel):
    url: str
    email: str
    token: str


@router.get("", response_model=list[IntegrationOut])
async def list_integrations(
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    user_id = current_user.get("sub")
    result = await db.execute(select(Integration).where(Integration.user_id == user_id))
    return list(result.scalars().all())


@router.post("/github", response_model=IntegrationOut)
async def save_github(
    body: GithubTokenRequest,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    user_id = current_user.get("sub")
    result = await db.execute(
        select(Integration).where(Integration.user_id == user_id, Integration.provider == "github")
    )
    existing = result.scalar_one_or_none()

    if existing:
        existing.token_encrypted = _encrypt(body.token)
        existing.connected = True
    else:
        existing = Integration(
            id=str(uuid.uuid4()),
            user_id=user_id,
            provider="github",
            token_encrypted=_encrypt(body.token),
        )
        db.add(existing)

    await db.commit()
    await db.refresh(existing)
    return existing


@router.post("/jira", response_model=IntegrationOut)
async def save_jira(
    body: JiraCredentialsRequest,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    user_id = current_user.get("sub")
    token_str = f"{body.email}:{body.token}"
    result = await db.execute(
        select(Integration).where(Integration.user_id == user_id, Integration.provider == "jira")
    )
    existing = result.scalar_one_or_none()

    if existing:
        existing.token_encrypted = _encrypt(token_str)
        existing.extra = {"url": body.url, "email": body.email}
        existing.connected = True
    else:
        existing = Integration(
            id=str(uuid.uuid4()),
            user_id=user_id,
            provider="jira",
            token_encrypted=_encrypt(token_str),
            extra={"url": body.url, "email": body.email},
        )
        db.add(existing)

    await db.commit()
    await db.refresh(existing)
    return existing


@router.post("/{provider}/test")
async def test_integration(
    provider: str,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    user_id = current_user.get("sub")
    result = await db.execute(
        select(Integration).where(Integration.user_id == user_id, Integration.provider == provider)
    )
    integration = result.scalar_one_or_none()
    if not integration:
        raise HTTPException(status_code=404, detail=f"No {provider} integration found")

    return {"status": "ok", "provider": provider, "connected": integration.connected}
