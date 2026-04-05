import os
import re
import psycopg
from dotenv import load_dotenv
import datetime

load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL")

REQUIRED_TEXT_KEYS = [
    "author_name",
    "department",
    "content",
]

REQUIRED_VALUE_KEYS = [
    "is_smooth",
    "work_start",
    "work_end",
]

OPTIONAL_TEXT_KEYS = [
    "improvement",
    "urgency",
    "notes",
]

ALL_KEYS = REQUIRED_TEXT_KEYS + REQUIRED_VALUE_KEYS + OPTIONAL_TEXT_KEYS

def normalize_text(value) -> str:
    if value is None:
        return ""
    if not isinstance(value, str):
        value = str(value)
    return re.sub(r"^[\u3000 \t]+|[\u3000 \t]+$", "", value)

def validate_and_prepare(data: dict):
    if not isinstance(data, dict):
        return None, "データ形式が違います"
    missing_keys = [key for key in ALL_KEYS if not key in data]
    if missing_keys:
        return None, f"項目が見つかりません。{', '.join(missing_keys)}"
    cleaned_data = {
        "author_name": normalize_text(data["author_name"]),
        "department": normalize_text(data["department"]),
        "content": normalize_text(data["content"]),
        "is_smooth": data["is_smooth"],
        "work_start": data["work_start"],
        "work_end": data["work_end"],
        "improvement": normalize_text(data["improvement"]),
        "urgency": normalize_text(data["urgency"]),
        "notes": normalize_text(data["notes"]),
    }
    missing_required = []

    for key in REQUIRED_TEXT_KEYS:
        if cleaned_data[key] == "":
            missing_required.append(key)
    for key in REQUIRED_VALUE_KEYS:
        if cleaned_data[key] is None:
            missing_required.append(key)

    if missing_required:
        return None, f"必須入力です。{', '.join(missing_required)}"
    return cleaned_data, None

# データベースに1件日報を登録する
def register_report(data: dict) -> dict:
    cleaned_data, error_message = validate_and_prepare(data)
    if error_message:
        return {"status": "error", "message": error_message}

    try:
        with psycopg.connect(DATABASE_URL) as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                        INSERT INTO public.reports (author_name, department, work_start, work_end, content, is_smooth, improvement, urgency, notes)
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                    """,
                    (
                        cleaned_data["author_name"],
                        cleaned_data["department"],
                        cleaned_data["work_start"],
                        cleaned_data["work_end"],
                        cleaned_data["content"],
                        cleaned_data["is_smooth"],
                        cleaned_data["improvement"],
                        cleaned_data["urgency"],
                        cleaned_data["notes"],
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
        return {"status": "error", "message": f"エラーが発生しました。{e}"}

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

data = {
    "author_name": "小林明",
    "department": "製造2課",
    "work_start":datetime.datetime.now(),
    "work_end":datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=9))),
    "content": "手袋の交換を依頼したが反応がない",
    "is_smooth": 3,
    "improvement": "ここが事故が起きやすい",
    "urgency": "中",
    "notes": "手袋は薄めのものを二重に付けると良い"
}
print(register_report(data))