import streamlit as st
from datetime import date, timedelta
from backend.database import get_must_read_reports

# 前日の日付を計算して表示用に使う
today = date.today()
target_date = today - timedelta(days=1)

st.title("現場レポート")
st.markdown(f"**📅 {target_date.strftime('%Y年%m月%d日')} のデータ**")

# ── session_stateの初期化 ──
if "selected_post" not in st.session_state:
    st.session_state.selected_post = None

# ── データ取得 ──
priority_posts, other_posts = get_must_read_reports()



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
                {post['department']}  {post['author_name']}
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
        work_start = str(post['work_start'])[:16].replace('T', ' ')
        work_end   = str(post['work_end'])[:16].replace('T', ' ')
        st.write(f"勤務時間：{work_start} 〜 {work_end}")
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