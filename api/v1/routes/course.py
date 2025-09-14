# api/v1/routes/course.py
from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from typing import List

from api.db.database import get_db
from ..schemas.course import CourseCreate, CourseResponse
from ..services.course import CourseService
from api.core.security import get_current_user 
from ..models.user import User 

router = APIRouter()

def get_course_service(db: Session = Depends(get_db)):
    """Dependency that provides a CourseService instance."""
    return CourseService(db)

@router.post("", response_model=List[CourseResponse], status_code=status.HTTP_201_CREATED)
def add_courses(
    course_names: List[CourseCreate],
    course_service: CourseService = Depends(get_course_service),
    current_user: User = Depends(get_current_user) 
):
    return course_service.create_courses(course_names=course_names, user_id=current_user.id)

@router.get("", response_model=List[CourseResponse])
def get_all_user_courses(
    course_service: CourseService = Depends(get_course_service),
    current_user: User = Depends(get_current_user)
):
    return course_service.retrieve_all_courses(current_user.id)