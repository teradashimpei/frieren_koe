import streamlit as st
from utils.api import get_summary, get_posts

st.title("今日の現場レポート")

# ── session_stateの初期化 ──
if "selected_post" not in st.session_state:
    st.session_state.selected_post = None

# ── ダミーデータ ──
all_posts = [
    {
        "id": 1,
        "author_name": "山田太郎",
        "department": "製造部",
        "content": "ラインCで異音が発生しました。原因は不明です。",
        "is_smooth": 1,
        "improvement": "設備点検が必要だと思います。",
        "urgency": "高",
        "notes": "早急に対応が必要だと感じました。",
        "work_start": "08:00",
        "work_end": "21:00",
    },
    {
        "id": 2,
        "author_name": "田中花子",
        "department": "営業部",
        "content": "クレーム対応に時間がかかりました。",
        "is_smooth": 2,
        "improvement": "対応マニュアルの見直しが必要です。",
        "urgency": "中",
        "notes": "",
        "work_start": "08:00",
        "work_end": "20:00",
    },
    {
        "id": 3,
        "author_name": "佐藤次郎",
        "department": "総務部",
        "content": "通常業務をこなしました。特に問題はありません。",
        "is_smooth": 4,
        "improvement": "",
        "urgency": "低",
        "notes": "",
        "work_start": "09:00",
        "work_end": "18:00",
    },
    {
        "id": 4,
        "author_name": "鈴木美咲",
        "department": "人事部",
        "content": "採用面接を3件実施しました。順調に進んでいます。",
        "is_smooth": 5,
        "improvement": "",
        "urgency": "低",
        "notes": "面接の雰囲気が良かったです。",
        "work_start": "09:00",
        "work_end": "17:30",
    },
    {
        "id": 5,
        "author_name": "伊藤健太",
        "department": "経理部",
        "content": "月次決算の資料作成を行いました。",
        "is_smooth": 3,
        "improvement": "",
        "urgency": "低",
        "notes": "",
        "work_start": "09:00",
        "work_end": "18:30",
    },
]

# ── 必読案件の判定 ──
def is_priority(post):
    try:
        start = int(post["work_start"].split(":")[0])
        end   = int(post["work_end"].split(":")[0])
        hours = end - start
    except:
        hours = 0
    return (
        post["is_smooth"] <= 2 or
        post["improvement"] != "" or
        post["urgency"] == "高" or
        hours >= 11
    )

priority_posts = [p for p in all_posts if is_priority(p)]
other_posts    = [p for p in all_posts if not is_priority(p)]

# ── 案件カード表示関数（expander版）──
def show_card(post, color):
    border_color = "#E24B4A" if color == "red" else "#B4B2A9"

    content_text     = f"順調度：{post['is_smooth']}　作業内容：{post['content'][:50]}"
    improvement_text = f"改善点：{post['improvement']}" if post['improvement'] else ""
    notes_text       = f"今日の気づき：{post['notes'][:50]}" if post['notes'] else ""

    extra = ""
    if improvement_text:
        extra += f"<br>{improvement_text}"
    if notes_text:
        extra += f"<br>{notes_text}"

    # カードのプレビュー
    st.markdown(
        f"""<div style="
            border-left: 4px solid {border_color};
            border-top: 0.5px solid #ddd;
            border-right: 0.5px solid #ddd;
            border-bottom: 0.5px solid #ddd;
            border-radius: 0 12px 12px 0;
            padding: 14px 16px;
            margin-bottom: 4px;
            background: white;">
            <div style="font-size:14px;font-weight:500;
                        margin-bottom:8px;">
                {post['author_name']}
            </div>
            <div style="font-size:13px;color:#666;
                        line-height:1.6;">
                {content_text}{extra}
            </div>
        </div>""",
        unsafe_allow_html=True
    )

    # expanderで詳細を表示
    with st.expander("詳細を見る"):
        st.write(f"部署名：{post['department']}")
        st.write(f"名前：{post['author_name']}")
        st.write(f"勤務時間：{post['work_start']} 〜 {post['work_end']}")
        st.divider()

        st.markdown("**作業内容**")
        st.text_area(
            label="作業内容",
            value=post["content"],
            disabled=True,
            label_visibility="collapsed",
            key=f"content_{post['id']}"
        )

        st.metric("順調度", post["is_smooth"])
        st.divider()

        st.markdown("**改善点**")
        st.text_area(
            label="改善点",
            value=post["improvement"] if post["improvement"] else "記載なし",
            disabled=True,
            label_visibility="collapsed",
            key=f"improvement_{post['id']}"
        )

        st.metric("緊急度", post["urgency"])
        st.divider()

        st.markdown("**今日の気づき**")
        st.text_area(
            label="今日の気づき",
            value=post["notes"] if post["notes"] else "記載なし",
            disabled=True,
            label_visibility="collapsed",
            key=f"notes_{post['id']}"
        )

# ── 案件一覧 ──
st.subheader("🚨 必読案件")
st.caption("順調度：2以下 / 改善点あり / 改善点緊急度：高 / 勤務時間11時間以上")

if priority_posts:
    for post in priority_posts:
        show_card(post, "red")
else:
    st.info("必読案件はありません")

st.subheader("📋 その他のレポート")

if other_posts:
    for post in other_posts:
        show_card(post, "gray")
else:
    st.info("その他のレポートはありません")