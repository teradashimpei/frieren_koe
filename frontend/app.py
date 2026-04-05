import streamlit as st

st.set_page_config(
    page_title="Koe",
    layout="centered",
    initial_sidebar_state="collapsed"
)

st.markdown("""
<style>
[data-testid="stSidebar"] { display: none; }
[data-testid="collapsedControl"] { display: none; }
</style>
""", unsafe_allow_html=True)

pages = {
    "": [
        st.Page("app_top.py",          title="TOP"),
        st.Page("pages/01_staff.py",   title="Staff"),
        st.Page("pages/02_manager.py", title="Manager"),
        st.Page("pages/03_search.py", title="Search"),
    ]
}

pg = st.navigation(pages)
pg.run()