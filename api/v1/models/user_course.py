# api/v1/models/user_course.py
import uuid
from sqlalchemy import Column, ForeignKey, DateTime, Integer
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from api.db.database import Base

class UserCourse(Base):
    __tablename__ = "user_courses"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    course_id = Column(UUID(as_uuid=True), ForeignKey("courses.id", ondelete="CASCADE"), nullable=False)
    
    last_studied_at = Column(DateTime(timezone=True))
    total_study_days = Column(Integer, default=0)
    
    user = relationship("User", back_populates="user_courses")
    course = relationship("Course", back_populates="user_courses")