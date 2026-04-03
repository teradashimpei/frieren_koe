import streamlit as st
from utils.api import get_summary, get_posts
from utils.ranking import SearchEngine

st.title("今日の現場レポート")

# ── session_stateの初期化 ──
if "selected_post" not in st.session_state:
    st.session_state.selected_post = None
if "show_ranking" not in st.session_state:
    st.session_state.show_ranking = False

# ── タブ ──
tab1, tab2 = st.tabs(["📋 案件一覧", "🔍 詳細"])

# ── タブ1：案件一覧 ──
with tab1:

    st.subheader("🚨 必読案件")
    st.caption("緊急度：高　または　上司判断あり")

    # ダミーデータ（バックエンドができたら差し替える）
    posts = [
        {"id": 1, "author_name": "田中太郎", "department": "製造部",
         "urgency": "高", "needs_manager": True,
         "content": "服が壊れたので買い替えが必要。",
         "status": "停滞", "memo": "早急に対応が必要です"},
        {"id": 2, "author_name": "佐藤花子", "department": "営業部",
         "urgency": "高", "needs_manager": False,
         "content": "ラインCで異音がした。",
         "status": "困っている", "memo": ""},
    ]

    for post in posts:
        col1, col2 = st.columns([3, 1])
        with col1:
            st.write(f"部署：{post['department']}　名前：{post['author_name']}")
            st.write(f"緊急度：{post['urgency']}　上司判断：{'あり' if post['needs_manager'] else 'なし'}")
        with col2:
            if st.button("詳細を見る", key=f"btn_{post['id']}"):
                st.session_state.selected_post = post
                st.session_state.show_ranking = False
        st.divider()

    st.subheader("📋 その他報告")
    st.info("バックエンド接続後に表示されます")

# ── タブ2：詳細 ──
with tab2:

    if st.session_state.selected_post is None:
        st.info("案件一覧から「詳細を見る」を押してください")

    else:
        post = st.session_state.selected_post

        st.subheader("必読案件の詳細")
        st.write(f"部署名：{post['department']}")
        st.write(f"名前：{post['author_name']}")
        st.divider()

        st.text_area(
            "報告書詳細",
            post["content"],
            disabled=True
        )

        col1, col2 = st.columns(2)
        col1.metric("緊急度", post["urgency"])
        col2.metric("進捗度", post["status"])

        if post["memo"]:
            st.caption(f"その他：{post['memo']}")

        st.divider()

        # 過去事例ボタン
        if st.button("過去事例を参照する"):
            st.session_state.show_ranking = True

        # 過去事例を表示
        if st.session_state.show_ranking:
            st.subheader("類似事例")
            keyword = st.text_input("キーワードを入力してください")
            if st.button("検索する"):
                st.info("バックエンド接続後に検索できます")