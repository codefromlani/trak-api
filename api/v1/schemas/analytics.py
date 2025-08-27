# api/v1/schemas/analytics.py
from pydantic import BaseModel, Field
from typing import List
from datetime import date

class CourseStudyDays(BaseModel):
    course_name: str = Field(..., description="The name of the course.")
    study_days: int = Field(..., description="The total number of days the course was studied.")

class AnalyticsResponse(BaseModel):
    course_study_data: List[CourseStudyDays]
    range_in_days: int
    start_date: date
    end_date: date