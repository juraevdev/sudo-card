from __future__ import annotations

from datetime import date

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session, joinedload

from ..database import get_db
from ..deps import require_scanner_key
from ..models import AccessCard, AccessLog
from ..schemas import VerifyRequest, VerifyResponse
from ..security import parse_qr_payload

router = APIRouter(prefix="/access", tags=["access"])


@router.post("/verify", response_model=VerifyResponse, dependencies=[Depends(require_scanner_key)])
def verify_access(body: VerifyRequest, db: Session = Depends(get_db)) -> VerifyResponse:
    token = parse_qr_payload(body.token)
    if not token:
        return _deny(db, None, None, "invalid_payload", body.gate, "Could not parse QR payload")

    card = (
        db.query(AccessCard)
        .options(joinedload(AccessCard.student))
        .filter(AccessCard.qr_token == token)
        .first()
    )
    if card is None:
        return _deny(db, None, token, "unknown_card", body.gate)

    student = card.student
    if card.revoked:
        return _deny(db, card.card_id, token, "revoked", body.gate, card.revoked_reason)

    if not student.is_active:
        return _deny(db, card.card_id, token, "student_inactive", body.gate)

    today = date.today()
    if today < card.issue_date:
        return _deny(db, card.card_id, token, "not_yet_valid", body.gate)

    if today > card.valid_until:
        return _deny(db, card.card_id, token, "expired", body.gate)

    _log(db, card.card_id, token, True, "ok", body.gate)
    return VerifyResponse(
        allowed=True,
        reason="ok",
        card_id=card.card_id,
        student_id=student.student_id,
        full_name=student.full_name,
        access=card.access_level,
    )


def _deny(
    db: Session,
    card_id: str | None,
    token: str | None,
    reason: str,
    gate: str | None,
    detail: str | None = None,
) -> VerifyResponse:
    _log(db, card_id, token, False, reason, gate, detail)
    return VerifyResponse(allowed=False, reason=reason, card_id=card_id)


def _log(
    db: Session,
    card_id: str | None,
    token: str | None,
    allowed: bool,
    reason: str,
    gate: str | None,
    detail: str | None = None,
) -> None:
    db.add(
        AccessLog(
            card_id=card_id,
            qr_token_prefix=(token[:8] if token else None),
            allowed=allowed,
            reason=reason,
            gate=gate,
            detail=detail,
        )
    )
    db.commit()
