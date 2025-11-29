from fastapi import APIRouter, status, Depends
from datetime import timedelta

from app.schemas.schemas import (
    UserRegisterRequest,
    UserLoginRequest,
    TokenResponse,
    UserResponse,
    LogoutResponse,
    MessageResponse,
)
from app.core.security import get_current_user


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
async def register(user_data: UserRegisterRequest) -> TokenResponse:
    """
    Register a new user account.
    
    - **email**: User email address (must be unique)
    - **password**: User password (minimum 8 characters)
    - **name**: User full name
    
    Returns JWT access token and user information.
    """
    pass


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
async def login(credentials: UserLoginRequest) -> TokenResponse:
    """
    Authenticate user and return JWT access token.
    
    - **email**: Registered user email
    - **password**: User password
    
    Returns JWT access token and user information.
    """
    pass


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
    pass


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
async def get_current_user_info(current_user: dict = Depends(get_current_user)) -> UserResponse:
    """
    Get the currently authenticated user's profile information.
    
    Requires valid JWT token.
    """
    pass
