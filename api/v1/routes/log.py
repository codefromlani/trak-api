# api/v1/routes/log.py
from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from typing import Dict, Any

from api.db.database import get_db
from ..schemas.course import LogCoursesRequest
from ..services.log import LogService
from api.core.security import get_current_user
from ..models.user import User

router = APIRouter()

def get_log_service(db: Session = Depends(get_db)):
    """Dependency that provides a LogService instance."""
    return LogService(db)

@router.post("", status_code=status.HTTP_200_OK, response_model=Dict[str, Any])
def log_study_sessions_endpoint(
    log_request: LogCoursesRequest,
    log_service: LogService = Depends(get_log_service),
    current_user: User = Depends(get_current_user)
):
    return log_service.log_study_sessions(current_user.id, log_request)