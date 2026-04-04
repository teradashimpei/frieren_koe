import requests

API_BASE_URL = "URLを入れる"

# 日報を送信する（01_staff.pyで使う）
def save_post(author_name, department, content,
              status, urgency, needs_manager, memo):
    
    data = {
        "author_name": author_name,
        "department": department,
        "content": content,
        "status": status,
        "urgency": urgency,
        "needs_manager": needs_manager,
        "memo": memo
    }
    
    response = requests.post(
        f"{API_BASE_URL}/voice/report",
        json=data
    )
    return response.json()


# AIサマリーを取得する（02_manager.pyで使う）
def get_summary():
    response = requests.get(
        f"{API_BASE_URL}/summary"
    )
    return response.json()


# 投稿一覧を取得する（02_manager.pyで使う）
def get_posts():
    response = requests.get(
        f"{API_BASE_URL}/summary/reports"
    )
    return response.json()