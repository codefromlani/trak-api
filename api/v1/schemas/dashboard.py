# api/v1/schemas/dashboard.py
from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class DashboardSummary(BaseModel):
    total_study_days: int
    current_streak: int
    most_studied_course: Optional[dict]

class ChecklistItem(BaseModel):
    course_name: str
    last_studied_at: Optional[datetime]