import streamlit as st

main_page = st.Page("dashboard.py", title="Dashboard")
page_2 = st.Page("model_overview.py", title="Model Overview")

pg = st.navigation([main_page, page_2], position="top")

pg.run()