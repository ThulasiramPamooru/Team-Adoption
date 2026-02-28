from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from pydantic import BaseModel
from typing import Optional
import uuid

from app.core.database import get_db
from app.core.auth import get_current_user
from app.models.user import User

router = APIRouter(prefix="/auth", tags=["auth"])


class UserOut(BaseModel):
    id: str
    email: str
    name: str
    role: str
    avatar: Optional[str]

    class Config:
        from_attributes = True


@router.get("/me", response_model=UserOut)
async def get_me(
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    auth0_id = current_user.get("sub")
    result = await db.execute(select(User).where(User.auth0_id == auth0_id))
    user = result.scalar_one_or_none()
    if not user:
        # Auto-create user in DEV_MODE
        from app.core.config import get_settings
        if get_settings().dev_mode:
            user = User(
                id=str(uuid.uuid4()),
                auth0_id=auth0_id,
                email=current_user.get("email", "admin@localhost.dev"),
                name=current_user.get("name", "Local Dev Admin"),
                role="admin",
            )
            db.add(user)
            await db.commit()
            await db.refresh(user)
            return user
        raise HTTPException(status_code=404, detail="User not found — call /auth/sync first")
    return user


@router.post("/sync", response_model=UserOut)
async def sync_user(
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """Create or update local user record from Auth0 payload."""
    auth0_id = current_user.get("sub")
    email = current_user.get("email", "")
    name = current_user.get("name") or current_user.get("nickname") or email
    avatar = current_user.get("picture")

    result = await db.execute(select(User).where(User.auth0_id == auth0_id))
    user = result.scalar_one_or_none()

    if user:
        user.email = email
        user.name = name
        user.avatar = avatar
    else:
        # First user becomes admin
        count_result = await db.execute(select(User))
        is_first = not count_result.scalars().first()
        user = User(
            id=str(uuid.uuid4()),
            auth0_id=auth0_id,
            email=email,
            name=name,
            avatar=avatar,
            role="admin" if is_first else "developer",
        )
        db.add(user)

    await db.commit()
    await db.refresh(user)
    return user
