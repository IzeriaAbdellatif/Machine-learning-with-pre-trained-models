from fastapi import APIRouter, status, Depends, HTTPException
from datetime import timedelta
from sqlalchemy.ext.asyncio import AsyncSession

from app.schemas.schemas import (
    UserRegisterRequest,
    UserLoginRequest,
    TokenResponse,
    UserResponse,
    LogoutResponse,
    MessageResponse,
    UserUpdateRequest,
)
from app.core.security import get_current_user
from app.db.session import get_session
from app.services import auth_service, user_service


router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post(
    "/register",
    response_model=TokenResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Register a new user",
    responses={
        201: {"description": "User successfully registered, token returned"},
        400: {"description": "Invalid input or email already exists"},
    },
)
async def register(user_data: UserRegisterRequest, db: AsyncSession = Depends(get_session)) -> TokenResponse:
    """
    Register a new user account.
    
    - **email**: User email address (must be unique)
    - **password**: User password (minimum 8 characters)
    - **name**: User full name
    - **Optional fields**: phone, location, bio, skills, soft_skills, preferred_locations, preferred_mode_travail, min_remuneration
    
    Returns JWT access token and user information.
    """
    # create user
    user = await user_service.create_user(
        db,
        email=user_data.email,
        password=user_data.password,
        name=user_data.name,
        phone=user_data.phone,
        location=user_data.location,
        bio=user_data.bio,
        skills=user_data.skills,
        soft_skills=user_data.soft_skills,
        preferred_locations=user_data.preferred_locations,
        preferred_mode_travail=user_data.preferred_mode_travail,
        min_remuneration=user_data.min_remuneration,
    )
    # create token
    access_token = auth_service.create_token_for_user(user)
    return TokenResponse(access_token=access_token, token_type="bearer", user=user)


@router.post(
    "/login",
    response_model=TokenResponse,
    status_code=status.HTTP_200_OK,
    summary="User login",
    responses={
        200: {"description": "Login successful, token returned"},
        401: {"description": "Invalid email or password"},
    },
)
async def login(credentials: UserLoginRequest, db: AsyncSession = Depends(get_session)) -> TokenResponse:
    """
    Authenticate user and return JWT access token.
    
    - **email**: Registered user email
    - **password**: User password
    
    Returns JWT access token and user information.
    """
    user = await auth_service.authenticate_user(db, credentials.email, credentials.password)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid email or password")
    access_token = auth_service.create_token_for_user(user)
    return TokenResponse(access_token=access_token, token_type="bearer", user=user)


@router.post(
    "/logout",
    response_model=LogoutResponse,
    status_code=status.HTTP_200_OK,
    summary="User logout",
    responses={
        200: {"description": "User successfully logged out"},
        401: {"description": "Unauthorized"},
    },
)
async def logout(current_user: dict = Depends(get_current_user)) -> LogoutResponse:
    """
    Logout the authenticated user.
    
    Requires valid JWT token. Token is invalidated on the client side.
    """
    # Token invalidation would require token store/blacklist. For now, client should discard token.
    return LogoutResponse(message="Successfully logged out")


@router.get(
    "/me",
    response_model=UserResponse,
    status_code=status.HTTP_200_OK,
    summary="Get current user",
    responses={
        200: {"description": "Current user information"},
        401: {"description": "Unauthorized or invalid token"},
    },
)
async def get_current_user_info(current_user: dict = Depends(get_current_user), db: AsyncSession = Depends(get_session)) -> UserResponse:
    """
    Get the currently authenticated user's profile information.
    
    Requires valid JWT token.
    """
    user_id = current_user.get("sub")
    if not user_id:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token payload")
    user = await user_service.get_user_by_id(db, user_id)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found")
    return user


@router.put(
    "/me",
    response_model=UserResponse,
    status_code=status.HTTP_200_OK,
    summary="Update current user profile",
    responses={
        200: {"description": "User profile successfully updated"},
        401: {"description": "Unauthorized or invalid token"},
    },
)
async def update_current_user(
    user_data: UserUpdateRequest,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_session)
) -> UserResponse:
    """
    Update the currently authenticated user's profile information.
    
    Supports updating:
    - name, phone, location, bio
    - skills, soft_skills (text)
    - preferred_locations, preferred_mode_travail (text)
    - min_remuneration
    
    Requires valid JWT token.
    """
    user_id = current_user.get("sub")
    if not user_id:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token payload")
    
    user = await user_service.get_user_by_id(db, user_id)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found")
    
    # Convert user_data to dict, excluding None values
    update_data = {k: v for k, v in user_data.model_dump().items() if v is not None}
    
    updated_user = await user_service.update_user(db, user, update_data)
    return updated_user
