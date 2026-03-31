from __future__ import annotations

from typing import List, Optional

from pydantic import BaseModel, EmailStr


class SmtpSendInput(BaseModel):
    host: str
    port: int
    use_tls: bool = True
    username_secret_key: str
    password_secret_key: str
    from_email: EmailStr
    to: List[EmailStr]
    subject: str
    body: str


class SmtpSendOutput(BaseModel):
    sent: bool
    message_id: Optional[str] = None

