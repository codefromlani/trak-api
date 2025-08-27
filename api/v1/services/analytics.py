# api/v1/services/analytics.py
from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import date, timedelta

from ..models.study_session import StudySession
from ..models.course import Course
from ..schemas.analytics import CourseStudyDays, AnalyticsResponse

class AnalyticsService:
    def __init__(self, db: Session):
        self.db = db

    def get_course_study_days(self, user_id: str, range_in_days: int) -> AnalyticsResponse:
        """
        Retrieves the number of study days per course for a user over a given date range.

        Args:
            user_id (str): The ID of the user.
            range_in_days (int): The number of days to look back.

        Returns:
            AnalyticsResponse: A Pydantic model containing the aggregated study data by course.
        """
        end_date = date.today()
        start_date = end_date - timedelta(days=range_in_days - 1)
        
        # Query to count the number of unique study days for each course
        study_data = (
            self.db.query(
                Course.name.label("course_name"),
                func.count(func.distinct(func.date(StudySession.date))).label("study_days_count")
            )
            .join(StudySession, StudySession.course_id == Course.id)
            .filter(
                StudySession.user_id == user_id,
                func.date(StudySession.date) >= start_date,
                func.date(StudySession.date) <= end_date
            )
            .group_by(Course.name)
            .order_by(func.count(func.distinct(func.date(StudySession.date))).desc())
            .all()
        )
        
        # Format the data into a list of CourseStudyDays
        course_data = [
            CourseStudyDays(
                course_name=row.course_name,
                study_days=row.study_days_count
            )
            for row in study_data
        ]
            
        return AnalyticsResponse(
            course_study_data=course_data,
            range_in_days=range_in_days,
            start_date=start_date,
            end_date=end_date
        )