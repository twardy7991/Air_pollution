import sys

sys.path.append("/opt/airflow/model/")

import torch
import pandas as pd
from datetime import datetime, timedelta
from my_postgres_hook import MyPostgresHook
from rnn_model import RNNModel

import numpy as np

def _recompute_model_predictions(timestamp_to_predict : datetime, model_name : str, conn_id : str = "POSTGRES_CONN_POLLUTION"):
    
    time_series_start = timestamp_to_predict - timedelta(hours=4)
    time_series_end = timestamp_to_predict 
    
    weather_df = _get_weather_data(conn_id=conn_id, 
                    time_series_start=time_series_start, 
                    time_series_end=time_series_end)
    
    time_series_start = timestamp_to_predict - timedelta(hours=24)
    time_series_end = timestamp_to_predict - timedelta(hours=1)
    
    pollution_df = _get_pollution_data(conn_id=conn_id, 
                    time_series_start=time_series_start, 
                    time_series_end=time_series_end
                    )
    
    df : pd.DataFrame = np.concatenate([weather_df, pollution_df], axis=1)
    
    model : RNNModel = torch.load(f"model/models/{model_name}")
    
    predictions = model(df)
    
    df_predictions = pd.DataFrame(predictions, columns=["predictions"])
    
    print(df)
    df_predictions["time"] = weather_df["time"]
    df_predictions["run"] = f"run_{str(datetime.now().date())}_{(datetime.now().time())}"
    
    df_predictions.set_index("run", inplace=True)
    
    _save_predictions(df_predictions)

    return 

def _get_weather_data(conn_id : str, time_series_start, time_series_end):
    return _get_data(conn_id, time_series_start, time_series_end, table="weather")

def _get_pollution_data(conn_id : str, time_series_start, time_series_end):
    return _get_data(conn_id, time_series_start, time_series_end, table="pollution")

def _get_data(conn_id : str, time_series_start, time_series_end, table):
    
    with MyPostgresHook(conn_id=conn_id).get_conn() as conn:
        
        if table == "pollution":
            cols = "pm2_5"
        
        df : pd.DataFrame = pd.read_sql(
            sql=f"""SELECT {cols} 
                    FROM {table}
                    WHERE time >= '{time_series_start}'
                    AND time < '{time_series_end}'
                    ORDER BY time""",
            con=conn)
    
    if table=="pollution":
        return df[["pm2_5"]]
    else:
        return df[
                    ['temperature_2m', 
                    'relative_humidity_2m', 
                    'dew_point_2m',
                    'apparent_temperature', 
                    'surface_pressure', 
                    'wind_speed_10m',
                    'wind_speed_80m', 
                    'wind_speed_120m', 
                    'wind_speed_180m',
                    'wind_direction_10m',
                    'wind_direction_80m', 
                    'wind_direction_120m',
                    'wind_direction_180m',
                    'wind_gusts_10m', 
                    'shortwave_radiation',
                    'direct_radiation', 
                    'diffuse_radiation', 
                    'vapour_pressure_deficit',
                    'precipitation', 
                    'snowfall', 
                    'freezing_level_height']
                ]
        
def _save_predictions(data : pd.DataFrame, conn_id : str) -> None:
        
    with MyPostgresHook(conn_id=conn_id).get_conn() as conn:
        
        data.to_sql(
            name="predictions",
            con=conn,
            if_exists="replace",
        )
        
    return 
    