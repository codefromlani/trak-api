from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from sqlalchemy.exc import IntegrityError
from typing import List

from ..schemas.course import CourseCreate
from ..models.course import Course
from ..models.user_course import UserCourse


class CourseService:
    def __init__(self, db: Session):
        self.db = db

    def create_courses(self, user_id: str, course_names: List[CourseCreate]) -> List[Course]:
        """Creates multiple courses and links them to the user via UserCourse."""
        created_courses = []

        try:
            for course in course_names:
                course_name = course.name.strip()

                # Skip empty names
                if not course_name:
                    continue

                existing_course = (
                    self.db.query(Course)
                    .join(UserCourse)
                    .filter(Course.name == course_name, UserCourse.user_id == user_id)
                    .first()
                )
                if existing_course:
                    raise HTTPException(
                        status_code=status.HTTP_409_CONFLICT,
                        detail=f"Course with name '{course_name}' already exists."
                    )

                db_course = Course(name=course_name)
                self.db.add(db_course)
                self.db.commit()
                self.db.refresh(db_course)

                user_course = UserCourse(user_id=user_id, course_id=db_course.id)
                self.db.add(user_course)
                self.db.commit()
                self.db.refresh(user_course)

                created_courses.append(db_course)

            return created_courses

        except IntegrityError:
            self.db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Database error while creating course."
            )

    def retrieve_all_courses(self) -> List[Course]:
        """Retrieves all courses."""
        return self.db.query(Course).order_by(Course.name).all()
