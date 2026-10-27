from __future__ import annotations

from datetime import date

from pydantic import BaseModel, ConfigDict, Field


class CamelModel(BaseModel):
    model_config = ConfigDict(populate_by_name=True, serialize_by_alias=True)


class LoginRequest(CamelModel):
    student_id: str = Field(alias="studentId", min_length=3, max_length=64)
    password: str = Field(min_length=4, max_length=128)


class TokenResponse(CamelModel):
    access_token: str = Field(serialization_alias="accessToken")
    token_type: str = Field(default="bearer", serialization_alias="tokenType")


class CardResponse(CamelModel):
    full_name: str = Field(serialization_alias="fullName")
    student_id: str = Field(serialization_alias="studentId")
    card_id: str = Field(serialization_alias="cardId")
    organization: str
    access: str
    issue_date: date = Field(serialization_alias="issueDate")
    valid_until: date = Field(serialization_alias="validUntil")
    # Compact payload to encode into the on-screen QR. Contains no PII.
    qr_payload: str = Field(serialization_alias="qrPayload")
    revoked: bool


class VerifyRequest(CamelModel):
    token: str = Field(min_length=8, max_length=256, description="Raw QR contents")
    gate: str | None = Field(default=None, max_length=64)


class VerifyResponse(CamelModel):
    allowed: bool
    reason: str
    card_id: str | None = Field(default=None, serialization_alias="cardId")
    student_id: str | None = Field(default=None, serialization_alias="studentId")
    full_name: str | None = Field(default=None, serialization_alias="fullName")
    access: str | None = None


class HealthResponse(BaseModel):
    status: str
    service: str
