from __future__ import annotations

from fastapi import Depends, Header, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from .config import get_settings
from .database import get_db
from .models import Student
from .security import decode_access_token

bearer = HTTPBearer(auto_error=False)


def get_current_student(
    creds: HTTPAuthorizationCredentials | None = Depends(bearer),
    db: Session = Depends(get_db),
) -> Student:
    if creds is None or creds.scheme.lower() != "bearer":
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated")
    student_id = decode_access_token(creds.credentials)
    if not student_id:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid or expired token")
    student = db.query(Student).filter(Student.student_id == student_id).first()
    if student is None or not student.is_active:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Student not found or inactive")
    return student


def require_scanner_key(x_scanner_key: str | None = Header(default=None, alias="X-Scanner-Key")) -> None:
    settings = get_settings()
    if not x_scanner_key or x_scanner_key != settings.scanner_api_key:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid scanner key")
