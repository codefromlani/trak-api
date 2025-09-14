# api/v1/services/dashboard.py
from sqlalchemy.orm import Session
from datetime import date, timedelta
from sqlalchemy import func
from typing import List, Dict, Any

from ..models.study_session import StudySession
from ..models.course import Course
from ..models.user_course import UserCourse
from ..schemas.dashboard import ChecklistItem

class DashboardService:
    def __init__(self, db: Session):
        self.db = db

    def get_total_study_days(self, user_id: str):
        """Calculates the total number of unique days a user has studied."""
        total_days = (
            self.db.query(func.count(func.distinct(func.date(StudySession.date))))
            .filter(StudySession.user_id == user_id)
            .scalar()
        )
        return total_days if total_days is not None else 0
    
    def get_current_streak(self, user_id: str):
        """Calculates the current consecutive study day streak."""
        today = date.today()
        
        study_dates = (
            self.db.query(func.date(StudySession.date))
            .filter(StudySession.user_id == user_id)
            .distinct()
            .order_by(func.date(StudySession.date).desc())
            .all()
        )
        
        study_dates = {d[0] for d in study_dates}
        
        if not study_dates:
            return 0
        
        current_date = today
        if current_date not in study_dates:
            current_date = today - timedelta(days=1)
            if current_date not in study_dates:
                return 0

        streak = 0
        while current_date in study_dates:
            streak += 1
            current_date -= timedelta(days=1)
            
        return streak
    
    def get_most_studied_course(self, user_id: str):
        """Finds the course the user has studied the most and its total days."""
        most_studied = (
            self.db.query(Course.name, UserCourse.total_study_days)
            .join(UserCourse)
            .filter(UserCourse.user_id == user_id, UserCourse.total_study_days > 0)
            .order_by(UserCourse.total_study_days.desc())
            .first()
        )
        if most_studied:
            return {
                "name": most_studied.name,
                "days": most_studied.total_study_days
            }
        return None
    
    def get_checklist_items(self, user_id: str) -> List[ChecklistItem]:
        """Retrieves the list of courses for the user with their last studied date."""
        checklist_data = (
            self.db.query(Course.name, UserCourse.last_studied_at)
            .join(UserCourse)
            .filter(UserCourse.user_id == user_id)
            .order_by(Course.name)
            .all()
        )
        
        # Convert the query results into a list of ChecklistItem objects
        return [
            ChecklistItem(course_name=name, last_studied_at=last_studied_at)
            for name, last_studied_at in checklist_data
        ]

    def get_recent_study_sessions(self, user_id: str, limit: int = 5) -> List[Dict[str, Any]]:
        """
        Retrieves a list of the most recent study sessions for a user.
        """
        recent_sessions = (
            self.db.query(StudySession.date, Course.name)
            .join(Course, StudySession.course_id == Course.id)
            .filter(StudySession.user_id == user_id)
            .order_by(StudySession.date.desc())
            .limit(limit)
            .all()
        )

        # Format the results into a list of dictionaries
        return [
            {"date": session_date, "course_name": course_name}
            for session_date, course_name in recent_sessions
        ]