from fastapi import APIRouter, HTTPException

from backend.database import fetch_all, fetch_one

router = APIRouter(prefix="/api/dashboard", tags=["Dashboard"])


@router.get("/summary")
def summary():
    try:
        return fetch_one("SELECT * FROM dashboard_summary")
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))


@router.get("/categories")
def categories():
    try:
        return fetch_all(
            "SELECT * FROM category_summary ORDER BY title_count DESC, category"
        )
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))


@router.get("/popular-books")
def popular_books():
    try:
        return fetch_all(
            "SELECT * FROM popular_books ORDER BY times_borrowed DESC, title LIMIT 10"
        )
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))
