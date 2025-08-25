# api/v1/routes/dashboard.py
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import Dict, Any, List

from api.db.database import get_db
from api.core.security import get_current_user
from ..services.dashboard import DashboardService
from ..models.user import User
from ..schemas.dashboard import ChecklistItem

router = APIRouter()

def get_dashboard_service(db: Session = Depends(get_db)):
    """Dependency that provides a DashboardService instance."""
    return DashboardService(db)

@router.get("/summary", response_model=Dict[str, Any])
def get_dashboard_summary(
    dashboard_service: DashboardService = Depends(get_dashboard_service), 
    current_user: User = Depends(get_current_user)
):
    total_study_days = dashboard_service.get_total_study_days(current_user.id)
    current_streak = dashboard_service.get_current_streak(current_user.id)
    most_studied_course = dashboard_service.get_most_studied_course(current_user.id)
    
    return {
        "total_study_days": total_study_days,
        "current_streak": current_streak,
        "most_studied_course": most_studied_course,
    }

@router.get("/checklist", response_model=List[ChecklistItem])
def get_dashboard_checklist(
    dashboard_service: DashboardService = Depends(get_dashboard_service),
    current_user: User = Depends(get_current_user)
):
    return dashboard_service.get_checklist_items(current_user.id)