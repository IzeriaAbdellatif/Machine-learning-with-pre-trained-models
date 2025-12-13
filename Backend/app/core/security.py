from datetime import datetime, timedelta, timezone
from typing import Optional

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import JWTError, jwt
from passlib.context import CryptContext

from app.core.config import settings


# Password hashing context
# Prefer `bcrypt_sha256` which first hashes the password with SHA-256
# before passing to bcrypt. This avoids the 72-byte bcrypt limit while
# remaining compatible with existing bcrypt hashes (bcrypt left in list).
pwd_context = CryptContext(schemes=["pbkdf2_sha256"], deprecated="auto")

# HTTP Bearer security scheme
security = HTTPBearer()


def hash_password(password: str) -> str:
    """Hash a password using bcrypt."""
    # Bcrypt has a 72-byte password limit. Truncate bytes safely to avoid
    # ValueError from the underlying bcrypt implementation while preserving
    # deterministic behavior for verification.
    def _truncate_password(p: str) -> str:
        b = p.encode("utf-8")
        if len(b) <= 72:
            return p
        # Truncate to 72 bytes and decode ignoring partial multibyte char at end
        return b[:72].decode("utf-8", errors="ignore")

    safe_password = _truncate_password(password)
    return pwd_context.hash(safe_password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a plain password against its hashed version."""
    # Apply the same truncation used when hashing so verification matches.
    b = plain_password.encode("utf-8")
    if len(b) > 72:
        plain_password = b[:72].decode("utf-8", errors="ignore")
    return pwd_context.verify(plain_password, hashed_password)


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """
    Create a JWT access token.
    
    Args:
        data: Dictionary containing claims to encode
        expires_delta: Optional timedelta for token expiration
        
    Returns:
        Encoded JWT token as string
    """
    to_encode = data.copy()
    
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(
            minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
        )
    
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(
        to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM
    )
    return encoded_jwt


async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)) -> dict:
    """
    Dependency to extract and validate JWT token from request.
    
    Args:
        credentials: HTTP Bearer credentials from request
        
    Returns:
        Decoded token payload containing user information
        
    Raises:
        HTTPException: If token is invalid or expired
    """
    credential_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        token = credentials.credentials
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        user_id: str = payload.get("sub")
        
        if user_id is None:
            raise credential_exception
            
    except JWTError:
        raise credential_exception
    
    return payload
