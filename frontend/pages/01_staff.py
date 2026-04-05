import streamlit as st
import datetime
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
        department = st.text_input("部署")
        author_name = st.text_input("名前")

        st.divider()

        # ① 作業時間
        st.subheader("⏰ 作業時間")
        start_time = st.time_input("作業開始時間", step=datetime.timedelta(minutes=1))
        end_time = st.time_input("作業終了時間", step=datetime.timedelta(minutes=1))        

        st.divider()

        # 業務内容
        st.markdown("### 📝 業務内容　<span style='color:red; font-size:14px;'>※必須</span>", unsafe_allow_html=True)
        content = st.text_area("本日の業務内容をお話しください",
                                placeholder="例：午前はラインAで部品の組み立て作業、午後は検査工程に入った。新しい部品の取り付けを初めてやった")
        # ② 順調ですか？（必須）
        st.markdown("### 📊 作業は順調ですか？　<span style='color:red; font-size:14px;'>※必須</span>", unsafe_allow_html=True)
        col_left, col_radio, col_right = st.columns([0.5, 8, 0.5])
        with col_left:
            st.markdown("<p style='text-align:right; margin-top:8px;'>停滞</p>", unsafe_allow_html=True)
        with col_radio:
            status = st.radio("", ["1", "2", "3", "4", "5"], horizontal=True)
        with col_right:
            st.markdown("<p style='text-align:left; margin-top:8px;'>順調</p>", unsafe_allow_html=True)
        
        st.divider()

        # ③ 改善点（任意）
        st.markdown("### 💡 改善点　<span style='color:gray; font-size:14px;'>※任意</span>", unsafe_allow_html=True)
        memo = st.text_area("改善点があればお話しください",
                    placeholder="例：工程の順番を変えたら時間が短縮できそう／この工具が古くて使いにくい／〇〇さんが体調悪そうだった")

        # 緊急度（改善点の子）
        urgency = st.radio("緊急度",
                           ["高", "中", "低"],
                           horizontal=True)

        st.divider()

        # ③ 気付いたこと（任意）
        st.markdown("### 💬 気付いたこと　<span style='color:gray; font-size:14px;'>※任意</span>", unsafe_allow_html=True)
        notice = st.text_area("業務以外のことでも、気になったことをお話しください",
                      placeholder="例：今日の材料がいつもより硬い気がする／ベテランの〇〇さんのやり方が参考になった／人手が足りなくて焦った／更衣室の鍵が壊れかけている")

        submitted = st.form_submit_button("送信する")

    # ── 送信処理 ──
    if submitted:
        if not author_name or not content or not status:
            st.error("名前・業務内容・順調ですか？は必須です")
        else:
            save_post(author_name, department, content,
                      status, urgency, False, memo,notice)
            st.success("送信完了しました！お疲れさまでした🍺")
