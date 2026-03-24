import streamlit as st
import pandas as pd
import os
import matplotlib.pyplot as plt
import altair as alt
import dotenv

from datetime import datetime

dotenv.load_dotenv(".env")
POSTGRES_URI = "postgresql://postgres:postgres@pollution_db:5472/pollution_db"#os.environ.get("POSTGRES_URI")

import logging

# class Race_df:
#     def __init__(self, race):
#         self.df = load_data(race)

logger = logging.getLogger()


def load_pollution_data():
    df = pd.read_sql(
        sql="""
            SELECT *
            FROM pollution
            ORDER BY time 
            LIMIT 24""",
        con=POSTGRES_URI,
    )
    
    logger.info("data updated")
    
    return df

def load_predictions_data():
    df = pd.read_sql(
        sql="""
            SELECT *
            FROM predictions
            ORDER BY time 
            LIMIT 24""",
        con=POSTGRES_URI,
    )
    
    logger.info("data updated")
    
    return df


def main():
    st.set_page_config(
        page_title="Air Pollution Dashboard",
        layout="wide"
    )
    
    st.title("Air Pollution Dashboard")
    
    st.markdown("""Project aims to predict pollution level for next 24 hours for Cracow city with help of Machine Learning. For now it only targets pm2_5, which is suspended
                dust with diameter less than 2.5 micrometer. It is more dangerous compared to the bigger ones as it enters bloodsteam and might cause
                serious health issues\n\n Currently only one model is available, which is a simple RNN, for specific details visit Model Overview""",
                width=1000)

    df_predictions : pd.DataFrame = load_predictions_data()
    
    df_pollution : pd.DataFrame = load_pollution_data()
    
    df = pd.concat([df_predictions, df_pollution], axis=0)
    

    df = pd.DataFrame(
        data=[
            [-1, 3, None],
            [0, 1, None],
            [1, 2, None],
            [2, 3, 3],
            [3, None, 5],
            [4, None, 3],
            [5, None, 5]
        ],
        columns=["time", "pm2_5", "pm2_5official"]
    )
    
    chart = alt.Chart(df).transform_fold(
    ['pm2_5official', 'pm2_5'],
    as_=['series', 'value']
    ).mark_line(interpolate="monotone").encode(
        x='time:T',
        y='value:Q',
        color=alt.Color(
        'series:N',
        title='PM Source',
        scale=alt.Scale(
            range=['lightblue', 'lightblue']
        ),
        ),
        strokeDash=alt.StrokeDash('series:N',         legend=alt.Legend(
            labelExpr="datum.label == 'pm2_5official' ? 'RNN predictions' : 'Historic level'"
        ))
    )
    
    date = datetime.now()
    st.write(f"Current datetime - :blue[{date}]")
    
    st.selectbox(label="Select Model", options=["RNN"], accept_new_options=False)
    
    st.write(chart)
    
if __name__ == "__main__":
    main()