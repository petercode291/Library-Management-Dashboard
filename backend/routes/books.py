from fastapi import APIRouter, HTTPException, Query

from backend.database import fetch_all, fetch_one, get_db
from backend.models.book import BookCreate, BookUpdate

router = APIRouter(prefix="/api/books", tags=["Books"])


@router.get("")
def list_books(search: str = Query(default="")):
    sql = """
        SELECT book_id, isbn, title, author, category, publisher,
               publication_year, total_copies, available_copies
        FROM books
        WHERE %s = ''
           OR title LIKE CONCAT('%%', %s, '%%')
           OR author LIKE CONCAT('%%', %s, '%%')
           OR category LIKE CONCAT('%%', %s, '%%')
        ORDER BY title
    """
    return fetch_all(sql, (search, search, search, search))


@router.get("/{book_id}")
def get_book(book_id: int):
    book = fetch_one(
        """SELECT book_id, isbn, title, author, category, publisher,
                  publication_year, total_copies, available_copies
           FROM books WHERE book_id = %s""",
        (book_id,),
    )
    if not book:
        raise HTTPException(status_code=404, detail="Book not found")
    return book


@router.post("", status_code=201)
def create_book(book: BookCreate):
    with get_db() as conn:
        cursor = conn.cursor(dictionary=True)
        try:
            cursor.execute(
                """INSERT INTO books
                   (isbn, title, author, category, publisher, publication_year,
                    total_copies, available_copies)
                   VALUES (%s,%s,%s,%s,%s,%s,%s,%s)""",
                (
                    book.isbn,
                    book.title,
                    book.author,
                    book.category,
                    book.publisher,
                    book.publication_year,
                    book.total_copies,
                    book.total_copies,
                ),
            )
            conn.commit()
            new_id = cursor.lastrowid
        except Exception as exc:
            conn.rollback()
            if getattr(exc, "errno", None) == 1062:
                raise HTTPException(status_code=409, detail="ISBN already exists")
            raise HTTPException(status_code=400, detail=str(exc))
        finally:
            cursor.close()

    return get_book(new_id)


@router.patch("/{book_id}")
def update_book(book_id: int, book: BookUpdate):
    existing = get_book(book_id)
    data = book.model_dump(exclude_unset=True)

    if not data:
        return existing

    # Keep the number of borrowed copies stable when total_copies changes.
    if "total_copies" in data:
        borrowed = existing["total_copies"] - existing["available_copies"]
        if data["total_copies"] < borrowed:
            raise HTTPException(
                status_code=400,
                detail=f"Cannot reduce total copies below {borrowed} borrowed copies.",
            )
        data["available_copies"] = data["total_copies"] - borrowed

    fields = []
    values = []
    allowed = {
        "isbn", "title", "author", "category", "publisher",
        "publication_year", "total_copies", "available_copies"
    }

    for key, value in data.items():
        if key in allowed:
            fields.append(f"{key} = %s")
            values.append(value)

    values.append(book_id)

    with get_db() as conn:
        cursor = conn.cursor()
        try:
            cursor.execute(
                f"UPDATE books SET {', '.join(fields)} WHERE book_id = %s",
                tuple(values),
            )
            conn.commit()
        except Exception as exc:
            conn.rollback()
            if getattr(exc, "errno", None) == 1062:
                raise HTTPException(status_code=409, detail="ISBN already exists")
            raise HTTPException(status_code=400, detail=str(exc))
        finally:
            cursor.close()

    return get_book(book_id)


@router.delete("/{book_id}")
def delete_book(book_id: int):
    get_book(book_id)

    with get_db() as conn:
        cursor = conn.cursor()
        try:
            cursor.execute("DELETE FROM books WHERE book_id = %s", (book_id,))
            conn.commit()
        except Exception as exc:
            conn.rollback()
            if getattr(exc, "errno", None) == 1451:
                raise HTTPException(
                    status_code=409,
                    detail="This book has loan history and cannot be deleted.",
                )
            raise HTTPException(status_code=400, detail=str(exc))
        finally:
            cursor.close()

    return {"message": "Book deleted"}
