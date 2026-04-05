import os
import re
import psycopg
from datetime import datetime, timezone, timedelta
from dotenv import load_dotenv
from psycopg.rows import dict_row

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

# 共通のDB接続設定
def get_connection():
    """辞書形式でデータを返す設定でDBに接続する"""
    return psycopg.connect(DATABASE_URL, row_factory=dict_row)

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
        with get_connection() as conn:
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
        return {"status": "error", "message": f"エラーが発生しました。"}

# データベースから日報のデータをすべて取得する
def get_all_reports() -> list:
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                "SELECT * FROM public.reports ORDER BY created_at DESC"
            )
            return cur.fetchall()

def get_today_reports() -> list[dict]:
    """今日（日本時間 0:00以降）のデータだけをDBから高速に取得する"""
    # 今日（日本時間）を作る
    jst = timezone(timedelta(hours=9))
    today_start = datetime.now(jst).replace(hour=0, minute=0, second=0, microsecond=0)

    # データベースと時間を変換
    today_start_utc = today_start.astimezone(timezone.utc)

    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                "SELECT * FROM public.reports WHERE created_at >= %s ORDER BY created_at DESC",
                (today_start_utc,)
            )
            return cur.fetchall()

def get_work_hours(row: dict) -> float | None:
    """開始時間と終了時間から作業時間を計算する(単位:時間)"""
    try:
        start = row.get("work_start")
        end = row.get("work_end")
        if not start or not end:
            return None

        # 差分を計算して秒から時間に変換
        duration = end - start
        return duration.total_seconds() / 3600
    except Exception:
        return None

def get_must_read_reasons(row: dict) -> list[str]:
    reasons = []

    # --- 順調度 ---
    if row.get("is_smooth") is not None and int(row["is_smooth"]) <= 2:
        reasons.append(f"順調度が低い（{row['is_smooth']}/5）")

    # --- 改善 ---
    if row.get("improvement") and str(row["improvement"]).strip():
        reasons.append("改善提案あり")

    # --- 緊急度 ---
    if row.get("urgency") == "高":
        reasons.append("本人が緊急と判断")

    # --- 11時間以上の長時間労働 ---
    hours = get_work_hours(row)
    if hours is not None and hours >= 11:
        reasons.append(f"長時間勤務（{hours:.1f}h）")

    return reasons

# データベースから指定した部署の日報を取得する
def get_reports_filter_department(department: str) -> list:
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                "SELECT * FROM public.reports WHERE department = %s",
                (department,)
            )
            return cur.fetchall()

def get_must_read_reports() -> list[dict]:
    """今日の日報から必読案件を抽出し、優先度順に並べて返す"""
    rows = get_today_reports()
    urgency_order = {"高": 0, "中": 1, "低": 2, None: 3}

    result = []
    for row in rows:
        reasons = get_must_read_reasons(row)
        if reasons:
            # 元のデータに「必読理由」を合体させてコピー
            result.append({**row, "must_read_reasons": reasons})

    # 優先度順（順調度 低い順 ＞ 緊急度 高い順）に並べ替え
    result.sort(key=lambda r: (
        int(r.get("is_smooth") or 5),
        urgency_order.get(r.get("urgency"), 3)
    ))
    return result
