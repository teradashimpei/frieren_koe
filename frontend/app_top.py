import streamlit as st

st.title("日報アプリ Koe")
st.write("どちらの画面を使いますか？")

if st.button("現場スタッフとしてログイン"):
    st.switch_page("pages/01_staff.py")

if st.button("管理者としてログイン"):
    st.switch_page("pages/02_manager.py")

# オレンジのボタン（遷移先は後で修正）
if st.button("気づきを見る", type="primary"):
    st.switch_page("pages/03_search.py")