from datetime import timedelta
from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.models import User
from app.core.security import verify_password, create_access_token


async def authenticate_user(db: AsyncSession, email: str, password: str):
    result = await db.execute(select(User).where(User.email == email))
    user = result.scalars().first()
    if not user:
        return None
    if not verify_password(password, user.hashed_password):
        return None
    return user


def create_token_for_user(user, expires_delta: timedelta = None):
    data = {"sub": str(user.id), "email": user.email}
    token = create_access_token(data, expires_delta=expires_delta)
    return token
