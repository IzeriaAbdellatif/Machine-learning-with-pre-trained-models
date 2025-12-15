from sqlalchemy import select, update, delete
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException, status

from app.models import User
from app.core.security import hash_password


async def get_user_by_id(db: AsyncSession, user_id: str):
    result = await db.execute(select(User).where(User.id == user_id))
    return result.scalars().first()


async def get_user_by_email(db: AsyncSession, email: str):
    result = await db.execute(select(User).where(User.email == email))
    return result.scalars().first()


async def create_user(
    db: AsyncSession,
    email: str,
    password: str,
    name: str,
    phone: str = None,
    location: str = None,
    bio: str = None,
    skills: str | list[str] = None,
    soft_skills: str | list[str] = None,
    preferred_locations: str | list[str] = None,
    preferred_mode_travail: str | list[str] = None,
    min_remuneration: float = None,
):
    hashed = hash_password(password)
    # Normalize lists to comma-separated strings for storage
    def _to_csv(val):
        if val is None:
            return None
        if isinstance(val, list):
            return ", ".join([str(s).strip() for s in val if str(s).strip()])
        return str(val)

    user = User(
        email=email,
        hashed_password=hashed,
        name=name,
        phone=phone,
        location=location,
        bio=bio,
        skills=_to_csv(skills),
        soft_skills=_to_csv(soft_skills),
        preferred_locations=_to_csv(preferred_locations),
        preferred_mode_travail=_to_csv(preferred_mode_travail),
        min_remuneration=min_remuneration,
    )
    db.add(user)
    try:
        await db.commit()
        await db.refresh(user)
        return user
    except IntegrityError:
        await db.rollback()
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email already registered")


async def update_user(db: AsyncSession, user: User, data: dict):
    for key, value in data.items():
        if hasattr(user, key) and value is not None:
            # Ensure lists are stored as comma-separated strings in the DB
            if isinstance(value, list):
                value = ", ".join([str(s).strip() for s in value if str(s).strip()])
            setattr(user, key, value)
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return user


async def delete_user(db: AsyncSession, user: User):
    await db.delete(user)
    await db.commit()
    return True
