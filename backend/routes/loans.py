from fastapi import APIRouter, HTTPException, Query

from backend.database import fetch_all, get_db
from backend.models.loan import LoanCreate

router = APIRouter(prefix="/api/loans", tags=["Loans"])


@router.get("")
def list_loans(active_only: bool = Query(default=False)):
    if active_only:
        return fetch_all(
            """SELECT l.loan_id, l.book_id, l.member_id,
                      b.title AS book_title,
                      CONCAT(m.first_name, ' ', m.last_name) AS member_name,
                      l.issue_date, l.due_date, l.return_date,
                      CASE
                        WHEN l.return_date IS NOT NULL THEN 'Returned'
                        WHEN l.due_date < CURRENT_DATE THEN 'Overdue'
                        ELSE 'Borrowed'
                      END AS status,
                      l.fine
               FROM loans l
               JOIN books b ON b.book_id = l.book_id
               JOIN members m ON m.member_id = l.member_id
               WHERE l.return_date IS NULL
               ORDER BY l.due_date"""
        )

    return fetch_all(
        """SELECT l.loan_id, l.book_id, l.member_id,
                  b.title AS book_title,
                  CONCAT(m.first_name, ' ', m.last_name) AS member_name,
                  l.issue_date, l.due_date, l.return_date,
                  CASE
                    WHEN l.return_date IS NOT NULL THEN 'Returned'
                    WHEN l.due_date < CURRENT_DATE THEN 'Overdue'
                    ELSE 'Borrowed'
                  END AS status,
                  l.fine
           FROM loans l
           JOIN books b ON b.book_id = l.book_id
           JOIN members m ON m.member_id = l.member_id
           ORDER BY l.issue_date DESC"""
    )


@router.get("/overdue")
def overdue_loans():
    return fetch_all(
        """SELECT * FROM overdue_books
           ORDER BY days_overdue DESC"""
    )


@router.post("", status_code=201)
def issue_book(loan: LoanCreate):
    with get_db() as conn:
        cursor = conn.cursor(dictionary=True)
        try:
            cursor.callproc("issue_book", (loan.book_id, loan.member_id, loan.days))
            result_sets = []
            for result in cursor.stored_results():
                result_sets.extend(result.fetchall())
            conn.commit()
            new_loan = result_sets[0] if result_sets else {}
        except Exception as exc:
            conn.rollback()
            message = getattr(exc, "msg", str(exc))
            raise HTTPException(status_code=400, detail=message)
        finally:
            cursor.close()

    return {
        "message": "Book issued successfully",
        "loan_id": new_loan.get("new_loan_id"),
    }


@router.post("/{loan_id}/return")
def return_book(loan_id: int):
    with get_db() as conn:
        cursor = conn.cursor(dictionary=True)
        try:
            cursor.callproc("return_book", (loan_id,))
            result_sets = []
            for result in cursor.stored_results():
                result_sets.extend(result.fetchall())
            conn.commit()
            result = result_sets[0] if result_sets else {}
        except Exception as exc:
            conn.rollback()
            message = getattr(exc, "msg", str(exc))
            raise HTTPException(status_code=400, detail=message)
        finally:
            cursor.close()

    return {
        "message": "Book returned successfully",
        "loan_id": result.get("loan_id"),
        "return_date": result.get("return_date"),
        "fine": float(result.get("fine", 0)),
    }
