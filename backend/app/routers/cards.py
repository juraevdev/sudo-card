from fastapi import APIRouter, Depends, HTTPException, status

from ..deps import get_current_student
from ..models import Student
from ..schemas import CardResponse
from ..security import build_qr_payload

router = APIRouter(prefix="/card", tags=["card"])


@router.get("/me", response_model=CardResponse)
def my_card(student: Student = Depends(get_current_student)) -> CardResponse:
    card = student.card
    if card is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No access card issued")
    return CardResponse(
        full_name=student.full_name,
        student_id=student.student_id,
        card_id=card.card_id,
        organization=card.organization,
        access=card.access_level,
        issue_date=card.issue_date,
        valid_until=card.valid_until,
        qr_payload=build_qr_payload(card.qr_token),
        revoked=card.revoked,
    )
