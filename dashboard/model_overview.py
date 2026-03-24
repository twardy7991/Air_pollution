import streamlit as st
import pandas as pd
import os
import matplotlib.pyplot as plt
import altair as alt
import dotenv

import logging

# class Race_df:
#     def __init__(self, race):
#         self.df = load_data(race)

logger = logging.getLogger()
    
def main():
    st.set_page_config(
        page_title="Model Architecture Overview",
        layout="wide"
    )
    
    st.title("Model Architecture Overview")
    
    st.markdown("""someday I will add something here""",
                width=1000)

if __name__ == "__main__":
    main()