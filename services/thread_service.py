from uuid import uuid4
from database.db import conn


def create_thread(user_id):

    thread_id = str(uuid4())

    with conn.cursor() as cur:

        cur.execute(
            """
            INSERT INTO threads(thread_id,user_id)
            VALUES(%s,%s)
            """,
            (thread_id, user_id)
        )

    return thread_id

def get_threads(user_id: str):

    with conn.cursor() as cur:

        cur.execute(
            """
            SELECT thread_id,title
            FROM threads
            WHERE user_id=%s
            ORDER BY updated_at DESC
            """,
            (user_id,)
        )

        rows = cur.fetchall()

    return rows

def update_thread(thread_id:str):
    with conn.cursor() as cur:
        cur.execute(
            """
            UPDATE threads
            SET updated_at = CURRENT_TIMESTAMP
            WHERE thread_id = %s
            """,
            (thread_id,)
            
        )
        
def update_title(thread_id: str, title: str):

    with conn.cursor() as cur:

        cur.execute(
            """
            UPDATE threads
            SET title=%s
            WHERE thread_id=%s
            """,
            (title, thread_id)
        )
        
def get_title(thread_id: str):

    with conn.cursor() as cur:

        cur.execute(
            """
            SELECT title
            FROM threads
            WHERE thread_id=%s
            """,
            (thread_id,)
        )

        row = cur.fetchone()

    if row:
        return row[0]

    return None             