import streamlit as st

st.title("Koe")
st.write("どちらの画面を使いますか？")

if st.button("現場スタッフとしてログイン"):
    st.switch_page("pages/01_staff.py")

if st.button("管理者としてログイン"):
    st.switch_page("pages/02_manager.py")