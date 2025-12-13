from fastapi import APIRouter, status, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.schemas.schemas import (
    UserResponse,
    UserUpdateRequest,
    MessageResponse,
)
from app.core.security import get_current_user
from app.db.session import get_session
from app.services import user_service


router = APIRouter(prefix="/users", tags=["User Profile"])


@router.get(
    "/{user_id}",
    response_model=UserResponse,
    status_code=status.HTTP_200_OK,
    summary="Get user profile",
    responses={
        200: {"description": "User profile retrieved"},
        404: {"description": "User not found"},
    },
)
async def get_user(user_id: str, db: AsyncSession = Depends(get_session)) -> UserResponse:
    """
    Get a user profile by ID.
    
    - **user_id**: The unique identifier of the user
    
    Returns user profile information including contact details and bio.
    """
    user = await user_service.get_user_by_id(db, user_id)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return user


@router.put(
    "/{user_id}",
    response_model=UserResponse,
    status_code=status.HTTP_200_OK,
    summary="Update user profile",
    responses={
        200: {"description": "User profile updated"},
        401: {"description": "Unauthorized"},
        404: {"description": "User not found"},
    },
)
async def update_user(
    user_id: str,
    update_data: UserUpdateRequest,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_session),
) -> UserResponse:
    """
    Update the authenticated user's profile information.
    
    Only the authenticated user can update their own profile.
    
    - **user_id**: The unique identifier of the user
    - **name**: Updated full name (optional)
    - **phone**: Updated phone number (optional)
    - **location**: Updated location (optional)
    - **bio**: Updated bio/summary (optional)
    
    Returns updated user profile.
    """
    # ensure authenticated user matches user_id
    sub = current_user.get("sub")
    if sub != user_id:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized to update this profile")
    user = await user_service.get_user_by_id(db, user_id)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    updated = await user_service.update_user(db, user, update_data.model_dump(exclude_none=True))
    return updated


@router.delete(
    "/{user_id}",
    response_model=MessageResponse,
    status_code=status.HTTP_200_OK,
    summary="Delete user account",
    responses={
        200: {"description": "User account deleted"},
        401: {"description": "Unauthorized"},
        404: {"description": "User not found"},
    },
)
async def delete_user(
    user_id: str,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_session),
) -> MessageResponse:
    """
    Delete a user account.
    
    Only the authenticated user can delete their own account.
    This action is irreversible.
    
    - **user_id**: The unique identifier of the user to delete
    
    Returns confirmation message.
    """
    sub = current_user.get("sub")
    if sub != user_id:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized to delete this account")
    user = await user_service.get_user_by_id(db, user_id)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    await user_service.delete_user(db, user)
    return MessageResponse(message="User account deleted")
