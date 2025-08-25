from sqlalchemy.orm import Session
from typing import Dict
from datetime import date, datetime
from sqlalchemy import func
from fastapi import HTTPException, status

from ..schemas.course import LogCoursesRequest
from ..models.user_course import UserCourse
from ..models.study_session import StudySession
from ..models.course import Course


class LogService:
    def __init__(self, db: Session):
        self.db = db

    def log_study_sessions(self, user_id: str, log_request: LogCoursesRequest) -> Dict:
        """Logs study sessions for multiple courses for a given user."""
        today = date.today()
        logged_courses_info =[]

        for course_name in log_request.course_names:
            course_name = course_name.strip()

            course = (
                self.db.query(Course)
                .filter(Course.name == course_name)
                .first()
            )

            if not course:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Course '{course_name}' not found."
                )

            user_course = self.db.query(UserCourse).filter_by(user_id=user_id, course_id=course.id).first()

            if not user_course:
                print(f"Warning: UserCourse link not found for user {user_id} and course {course_name}. Creating it.")
                user_course = UserCourse(user_id=user_id, course_id=course.id)
                self.db.add(user_course)
                self.db.flush()

            existing_session_today = (
                self.db.query(StudySession)
                .filter(
                    StudySession.user_id ==  user_id,
                    StudySession.course_id == course.id,
                    func.date(StudySession.date) == today
                ).first()
            )

            if not existing_session_today:
                # Only create a new session if one doesn't exist for today
                new_session = StudySession(
                    user_id=user_id,
                    course_id=course.id,
                    date=datetime.now(),
                )
                self.db.add(new_session)

                # Only increment total_study_days for the first log of the day
                user_course.total_study_days = (user_course.total_study_days or 0) + 1

                logged_courses_info.append(str(course_name))
                
            user_course.last_studied_at = datetime.now()

        self.db.commit()
        
        return {"message": "Study sessions logged successfully.", "logged_courses": logged_courses_info}