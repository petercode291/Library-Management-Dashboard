from datetime import date
from typing import Optional

from pydantic import BaseModel, Field


class LoanCreate(BaseModel):
    book_id: int = Field(gt=0)
    member_id: int = Field(gt=0)
    days: int = Field(default=14, ge=1, le=60)


class LoanOut(BaseModel):
    loan_id: int
    book_id: int
    member_id: int
    book_title: str
    member_name: str
    issue_date: date
    due_date: date
    return_date: Optional[date] = None
    status: str
    fine: float
