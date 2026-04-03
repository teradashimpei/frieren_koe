import os
import psycopg
from dotenv import load_dotenv

load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL")

# データベースに1件日報を登録する
def register_report(data: dict) -> dict:
    try:
        with psycopg.connect(DATABASE_URL) as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                        INSERT INTO public.reports (author_name, department, content, urgency, needs_manager, status)
                        VALUES (%s, %s, %s, %s, %s, %s)
                    """,
                    (data["author_name"], data["department"], data["content"], data["urgency"], data["needs_manager"], data["status"])
                )
                conn.commit()
        return {"status": "success", "message": "登録が完了しました"}
    except Exception as e:
        return {"status": "failed", "message": "登録に失敗しました"}

# データベースから日報のデータをすべて取得する
def get_all_reports() -> list:
    with psycopg.connect(DATABASE_URL) as conn:
        with conn.cursor() as cur:
            cur.execute(
                "SELECT * FROM public.reports WHERE author_name = '小林明'"
            )
            return cur.fetchall()


