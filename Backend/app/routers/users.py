from fastapi import APIRouter, status, Depends

from app.schemas.schemas import (
    UserResponse,
    UserUpdateRequest,
    MessageResponse,
)
from app.core.security import get_current_user


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
async def get_user(user_id: str) -> UserResponse:
    """
    Get a user profile by ID.
    
    - **user_id**: The unique identifier of the user
    
    Returns user profile information including contact details and bio.
    """
    pass


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
) -> UserResponse:
    """
    Update the authenticated user's profile information.
    
    Only the authenticated user can update their own profile.
    
    - **user_id**: The unique identifier of the user
    - **full_name**: Updated full name (optional)
    - **phone**: Updated phone number (optional)
    - **location**: Updated location (optional)
    - **bio**: Updated bio/summary (optional)
    
    Returns updated user profile.
    """
    pass


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
) -> MessageResponse:
    """
    Delete a user account.
    
    Only the authenticated user can delete their own account.
    This action is irreversible.
    
    - **user_id**: The unique identifier of the user to delete
    
    Returns confirmation message.
    """
    pass
