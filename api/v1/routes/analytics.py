# api/v1/routes/analytics.py
from fastapi import APIRouter, Depends, Query, status, HTTPException
from sqlalchemy.orm import Session

from api.db.database import get_db
from ..services.analytics import AnalyticsService
from api.core.security import get_current_user
from ..schemas.analytics import AnalyticsResponse
from ..models.user import User

router = APIRouter()

def get_analytics_service(db: Session = Depends(get_db)):
    """Dependency that provides an AnalyticsService instance."""
    return AnalyticsService(db)

@router.get("", response_model=AnalyticsResponse, status_code=status.HTTP_200_OK)
def get_analytics_data(
    range: str = Query("30d", description="Date range for analytics (e.g., '7d', '30d', '90d')."),
    analytics_service: AnalyticsService = Depends(get_analytics_service),
    current_user: User = Depends(get_current_user)
):
    # Parse the 'range' query parameter
    try:
        if range.endswith("d"):
            range_in_days = int(range[:-1])
        else:
            raise ValueError
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid date range format. Use 'Xd' where X is a number (e.g., '7d')."
        )
    
    return analytics_service.get_course_study_days(current_user.id, range_in_days)