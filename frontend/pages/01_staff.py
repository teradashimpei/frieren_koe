import streamlit as st
from utils.api import save_post

st.markdown("<h1 style='text-align: center;'>今日もお疲れさまでした 👷</h1>", unsafe_allow_html=True)

# ── スマホ風に中央寄せ ──
col1, col2, col3 = st.columns([1, 2, 1])

with col2:

    # ── session_stateの初期化 ──
    if "submitted" not in st.session_state:
        st.session_state.submitted = False

    # ── 入力フォーム ──
    with st.form("report_form"):

        # 基本情報
        st.subheader("👤 基本情報")
        author_name = st.text_input("名前")
        department = st.text_input("部署")

        st.divider()

        # 業務内容
        st.subheader("📝 業務内容")
        content = st.text_area("本日の業務内容をお話しください",
                                placeholder="例：作業内容")

        st.divider()

        # 状況確認
        st.subheader("📊 状況確認")
        status = st.radio("順調ですか？",
                         ["順調", "少し遅れ", "困っている", "停滞"])

        urgency = st.radio("緊急度は？",
                         ["高", "中", "低"])

        needs_manager = st.radio("上司の判断が必要ですか？",
                                ["はい", "いいえ"])

        st.divider()

        # その他
        st.subheader("💬 気づいたこと、改善点など")
        memo = st.text_area("ご自分の業務以外のことでもお話しください",
                            placeholder="例：〜〜")

        submitted = st.form_submit_button("送信する")

    # ── 送信処理 ──
    if submitted:
        if not author_name or not content:
            st.error("名前と業務内容は必須です")
        else:
            save_post(author_name, department, content,
                    status, urgency, needs_manager == "はい", memo)
            st.success("送信完了しました！お疲れさまでした 🍺")
