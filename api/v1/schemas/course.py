# api/v1/schemas/course.py
from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional, List
import uuid

class CourseCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)

class CourseResponse(BaseModel):
    id: uuid.UUID
    name: str
    created_at: datetime
    updated_at: Optional[datetime]

    class Config:
        from_attributes = True 

class LogCoursesRequest(BaseModel):
    course_names: List[str] = Field(..., min_items=1)