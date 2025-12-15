import uuid
from datetime import datetime, timezone
from typing import List, Optional

from sqlalchemy import (
    Column,
    String,
    Text,
    Float,
    DateTime,
    Integer,
    ForeignKey,
    UniqueConstraint,
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import relationship

from app.db.session import Base


def gen_uuid() -> str:
    return str(uuid.uuid4())


def get_utc_now() -> datetime:
    return datetime.now(timezone.utc)


class User(Base):
    __tablename__ = "users"

    id = Column(String, primary_key=True, default=gen_uuid)
    email = Column(String, unique=True, index=True, nullable=False)
    name = Column(String, nullable=False)
    hashed_password = Column(String, nullable=False)
    phone = Column(String, nullable=True)
    location = Column(String, nullable=True)
    bio = Column(Text, nullable=True)
    skills = Column(Text, nullable=True)  # Technical skills (comma-separated)
    soft_skills = Column(Text, nullable=True)  # Soft skills (comma-separated)
    preferred_locations = Column(Text, nullable=True)  # Preferred work locations (comma-separated)
    preferred_mode_travail = Column(Text, nullable=True)  # Preferred work modes (comma-separated)
    min_remuneration = Column(Float, nullable=True)  # Minimum expected salary
    created_at = Column(DateTime(timezone=True), default=get_utc_now)
    updated_at = Column(DateTime(timezone=True), default=get_utc_now, onupdate=get_utc_now)

    saved_jobs = relationship("SavedJob", back_populates="user", cascade="all, delete-orphan", lazy="selectin")


class Job(Base):
    __tablename__ = "jobs"

    id = Column(String, primary_key=True, default=gen_uuid)  # Auto-generated UUID
    title = Column(String, nullable=False)
    company = Column(String, nullable=False)
    location = Column(String, nullable=False)
    job_type = Column(String, nullable=True)
    experience_level = Column(String, nullable=True)
    description = Column(Text, nullable=True)
    required_skills = Column(JSONB, nullable=True)
    salary_min = Column(Float, nullable=True)
    salary_max = Column(Float, nullable=True)
    currency = Column(String, nullable=True)
    posted_at = Column(DateTime(timezone=True), nullable=True)
    deadline = Column(DateTime(timezone=True), nullable=True)
    
    # Indeed-specific fields
    job_url = Column(String, nullable=True, unique=True, index=True)  # Unique to prevent duplicates
    apply_url = Column(String, nullable=True)
    mode_travail = Column(String, nullable=True)  # remote/hybrid/presentiel
    remuneration = Column(String, nullable=True)  # Free text salary info
    missions_principales = Column(JSONB, nullable=True)  # Main missions array
    search_keyword = Column(String, nullable=True)  # Search term that found this job
    
    # ML scoring fields (for analytics/ranking)
    score_embedding = Column(Float, nullable=True)
    score_final = Column(Float, nullable=True)
    score_cross_encoder = Column(Float, nullable=True)

    saved_by = relationship("SavedJob", back_populates="job", cascade="all, delete-orphan", lazy="selectin")


class SavedJob(Base):
    __tablename__ = "saved_jobs"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(String, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    job_id = Column(String, ForeignKey("jobs.id", ondelete="CASCADE"), nullable=False)
    saved_at = Column(DateTime(timezone=True), default=get_utc_now)

    user = relationship("User", back_populates="saved_jobs", lazy="selectin")
    job = relationship("Job", back_populates="saved_by", lazy="selectin")
