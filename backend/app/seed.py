from __future__ import annotations

from datetime import date

from sqlalchemy.orm import Session

from .models import AccessCard, Student
from .security import hash_password, new_qr_token


def seed_if_empty(db: Session) -> None:
    if db.query(Student).first() is not None:
        return

    student = Student(
        student_id="SA-104237",
        full_name="Murodov Behruz",
        password_hash=hash_password("park2026"),
        is_active=True,
    )
    db.add(student)
    db.flush()

    db.add(
        AccessCard(
            card_id="UZN-2026-0142",
            student_pk=student.id,
            organization="JizPi IT PARK",
            access_level="STUDENT",
            issue_date=date(2026, 10, 5),
            valid_until=date(2027, 10, 5),
            qr_token=new_qr_token(),
            revoked=False,
        )
    )
    db.commit()
