import os
import re
import psycopg
from dotenv import load_dotenv

load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL")

# 必須項目がデータにあるかをチェックする
def validate_data(data: dict) -> list:
    require_keys = [
        "author_name",
        "department",
        "content",
        "urgency",
        "status"
    ]
    require_bool_keys = [
        "needs_manager",
    ]
    missing_keys = []
    for key in require_keys:
        value = data.get(key)
        if value is None or not re.sub(r"[\u3000 \t]", "", value):
            missing_keys.append(key)
    for bool_key in require_bool_keys:
        if data.get(bool_key) is None:
            missing_keys.append(bool_key)
    return missing_keys

# データベースに1件日報を登録する
def register_report(data: dict) -> dict:
    if not isinstance(data, dict):
        return {"status": "error", "message": "データ形式が違います"}

    missing_keys = validate_data(data)
    if missing_keys:
        return {"status": "error", "message": f"必須入力です。{(', ').join(missing_keys)}"}

    try:
        with psycopg.connect(DATABASE_URL) as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                        INSERT INTO public.reports (author_name, department, content, urgency, needs_manager, status, memo)
                        VALUES (%s, %s, %s, %s, %s, %s, %s)
                    """,
                    (
                        re.sub(r"[\u3000 \t]", "", data["author_name"]),
                        re.sub(r"[\u3000 \t]", "", data["department"]),
                        re.sub(r"[\u3000 \t]", "", data["content"]),
                        re.sub(r"[\u3000 \t]", "", data["urgency"]),
                        data["needs_manager"],
                        re.sub(r"[\u3000 \t]", "", data["status"]),
                        re.sub(r"[\u3000 \t]", "", data["memo"]),
                    )
                )
                conn.commit()
        return {"status": "success", "message": "登録が完了しました。"}
    except psycopg.OperationalError:
        return {"status": "error", "message": "データベース接続でエラーが発生しました。"}
    except psycopg.IntegrityError:
        return {"status": "error", "message": "登録に失敗しました。"}
    except psycopg.DatabaseError:
        return {"status": "error", "message": "データベース処理でエラーが発生しました。"}
    except Exception as e:
        return {"status": "error", "message": "エラーが発生しました。"}

# データベースから日報のデータをすべて取得する
def get_all_reports() -> list:
    with psycopg.connect(DATABASE_URL) as conn:
        with conn.cursor() as cur:
            cur.execute(
                "SELECT * FROM public.reports"
            )
            return cur.fetchall()

# データベースから指定した部署の日報を取得する
def get_reports_filter_department(department: str) -> list:
    with psycopg.connect(DATABASE_URL) as conn:
        with conn.cursor() as cur:
            cur.execute(
                "SELECT * FROM public.reports WHERE department = %s",
                (department,)
            )
            return cur.fetchall()
