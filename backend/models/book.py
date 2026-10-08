from typing import Optional

from pydantic import BaseModel, Field


class BookCreate(BaseModel):
    isbn: str = Field(min_length=1, max_length=20)
    title: str = Field(min_length=1, max_length=150)
    author: str = Field(min_length=1, max_length=100)
    category: str = Field(min_length=1, max_length=50)
    publisher: Optional[str] = Field(default=None, max_length=100)
    publication_year: Optional[int] = Field(default=None, ge=1000, le=9999)
    total_copies: int = Field(default=1, ge=1)


class BookUpdate(BaseModel):
    isbn: Optional[str] = Field(default=None, min_length=1, max_length=20)
    title: Optional[str] = Field(default=None, min_length=1, max_length=150)
    author: Optional[str] = Field(default=None, min_length=1, max_length=100)
    category: Optional[str] = Field(default=None, min_length=1, max_length=50)
    publisher: Optional[str] = Field(default=None, max_length=100)
    publication_year: Optional[int] = Field(default=None, ge=1000, le=9999)
    total_copies: Optional[int] = Field(default=None, ge=1)


class BookOut(BookCreate):
    book_id: int
    available_copies: int
