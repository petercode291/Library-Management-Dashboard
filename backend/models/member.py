from datetime import date
from typing import Optional

from pydantic import BaseModel, EmailStr, Field


class MemberCreate(BaseModel):
    member_code: str = Field(min_length=1, max_length=20)
    first_name: str = Field(min_length=1, max_length=50)
    last_name: str = Field(min_length=1, max_length=50)
    email: EmailStr
    phone: Optional[str] = Field(default=None, max_length=15)
    address: Optional[str] = Field(default=None, max_length=200)
    membership_date: Optional[date] = None
    status: str = Field(default="Active", pattern="^(Active|Inactive)$")


class MemberUpdate(BaseModel):
    first_name: Optional[str] = Field(default=None, min_length=1, max_length=50)
    last_name: Optional[str] = Field(default=None, min_length=1, max_length=50)
    email: Optional[EmailStr] = None
    phone: Optional[str] = Field(default=None, max_length=15)
    address: Optional[str] = Field(default=None, max_length=200)
    status: Optional[str] = Field(default=None, pattern="^(Active|Inactive)$")


class MemberOut(MemberCreate):
    member_id: int
