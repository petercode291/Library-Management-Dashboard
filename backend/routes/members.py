from fastapi import APIRouter, HTTPException, Query

from backend.database import fetch_all, fetch_one, get_db
from backend.models.member import MemberCreate, MemberUpdate

router = APIRouter(prefix="/api/members", tags=["Members"])


@router.get("")
def list_members(search: str = Query(default="")):
    sql = """
        SELECT member_id, member_code, first_name, last_name, email,
               phone, address, membership_date, status
        FROM members
        WHERE %s = ''
           OR member_code LIKE CONCAT('%%', %s, '%%')
           OR first_name LIKE CONCAT('%%', %s, '%%')
           OR last_name LIKE CONCAT('%%', %s, '%%')
           OR email LIKE CONCAT('%%', %s, '%%')
        ORDER BY first_name, last_name
    """
    return fetch_all(sql, (search, search, search, search, search))


@router.get("/{member_id}")
def get_member(member_id: int):
    member = fetch_one(
        """SELECT member_id, member_code, first_name, last_name, email,
                  phone, address, membership_date, status
           FROM members WHERE member_id = %s""",
        (member_id,),
    )
    if not member:
        raise HTTPException(status_code=404, detail="Member not found")
    return member


@router.post("", status_code=201)
def create_member(member: MemberCreate):
    with get_db() as conn:
        cursor = conn.cursor()
        try:
            cursor.execute(
                """INSERT INTO members
                   (member_code, first_name, last_name, email, phone, address,
                    membership_date, status)
                   VALUES (%s,%s,%s,%s,%s,%s,COALESCE(%s,CURRENT_DATE),%s)""",
                (
                    member.member_code,
                    member.first_name,
                    member.last_name,
                    member.email,
                    member.phone,
                    member.address,
                    member.membership_date,
                    member.status,
                ),
            )
            conn.commit()
            new_id = cursor.lastrowid
        except Exception as exc:
            conn.rollback()
            if getattr(exc, "errno", None) == 1062:
                raise HTTPException(
                    status_code=409,
                    detail="Member code or email already exists.",
                )
            raise HTTPException(status_code=400, detail=str(exc))
        finally:
            cursor.close()

    return get_member(new_id)


@router.patch("/{member_id}")
def update_member(member_id: int, member: MemberUpdate):
    get_member(member_id)
    data = member.model_dump(exclude_unset=True)

    if not data:
        return get_member(member_id)

    fields = []
    values = []
    for key, value in data.items():
        fields.append(f"{key} = %s")
        values.append(value)

    values.append(member_id)

    with get_db() as conn:
        cursor = conn.cursor()
        try:
            cursor.execute(
                f"UPDATE members SET {', '.join(fields)} WHERE member_id = %s",
                tuple(values),
            )
            conn.commit()
        except Exception as exc:
            conn.rollback()
            if getattr(exc, "errno", None) == 1062:
                raise HTTPException(status_code=409, detail="Email already exists.")
            raise HTTPException(status_code=400, detail=str(exc))
        finally:
            cursor.close()

    return get_member(member_id)
