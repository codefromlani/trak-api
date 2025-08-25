# api/v1/models/course.py
import uuid
from sqlalchemy import Column, String, DateTime
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from api.db.database import Base

class Course(Base):
    __tablename__ = "courses"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    name = Column(String, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    user_courses = relationship("UserCourse", back_populates="course", cascade="all, delete-orphan")
    study_sessions = relationship("StudySession", back_populates="course", cascade="all, delete-orphan")