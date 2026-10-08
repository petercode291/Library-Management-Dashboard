import os
from contextlib import contextmanager

import mysql.connector
from mysql.connector import pooling
from dotenv import load_dotenv

load_dotenv()

DB_CONFIG = {
    "host": os.getenv("DB_HOST", "localhost"),
    "port": int(os.getenv("DB_PORT", "3306")),
    "user": os.getenv("DB_USER", "root"),
    "password": os.getenv("DB_PASSWORD", ""),
    "database": os.getenv("DB_NAME", "library_management"),
}

_pool = None


def get_pool():
    global _pool
    if _pool is None:
        _pool = pooling.MySQLConnectionPool(
            pool_name="library_pool",
            pool_size=5,
            pool_reset_session=True,
            **DB_CONFIG,
        )
    return _pool


@contextmanager
def get_db():
    connection = get_pool().get_connection()
    try:
        yield connection
    finally:
        connection.close()


def fetch_all(query, params=None):
    with get_db() as conn:
        cursor = conn.cursor(dictionary=True)
        try:
            cursor.execute(query, params or ())
            return cursor.fetchall()
        finally:
            cursor.close()


def fetch_one(query, params=None):
    with get_db() as conn:
        cursor = conn.cursor(dictionary=True)
        try:
            cursor.execute(query, params or ())
            return cursor.fetchone()
        finally:
            cursor.close()
