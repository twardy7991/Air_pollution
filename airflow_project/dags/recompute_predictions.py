import sys

sys.path.append("/opt/airflow/model/")

import torch
import pandas as pd
from datetime import datetime, timedelta
from my_postgres_hook import MyPostgresHook
from rnn_model import RNNModel

import numpy as np
import logging

logger = logging.getLogger(__name__)
logger.setLevel("INFO")

def _predict(prediction_len : int, model, df, weather_predictions) -> np.ndarray:

    pred_list : np.ndarray = np.array()
    
    for i in range(prediction_len):         
        predictions = model(df)
        new_data = torch.tensor(np.concatenate([weather_predictions[i,:], predictions]))
        
def _recompute_model_predictions(timestamp_to_predict : datetime, model_name : str, conn_id : str = "POSTGRES_CONN_POLLUTION"):
    
    time_series_start = timestamp_to_predict - timedelta(hours=24)
    time_series_end = timestamp_to_predict 
    
    logger.info("fetching weather data for %s -  %s", str(time_series_start), str(time_series_end))
    
    weather_df = _get_weather_data(conn_id=conn_id, 
                    time_series_start=time_series_start, 
                    time_series_end=time_series_end)
    
    time_series_start = timestamp_to_predict
    time_series_end = timestamp_to_predict + timedelta(hours=24)
    
    logger.info("fetching weather_predictions data for %s -  %s", str(time_series_start), str(time_series_end))
    
    weather_prediction_df = _get_weather_data(
        conn_id=conn_id,
        time_series_start=time_series_start,
        time_series_end=time_series_end
    )
    
    time_series_start = timestamp_to_predict - timedelta(hours=25)
    time_series_end = timestamp_to_predict - timedelta(hours=1)
    
    logger.info("fetching pollution data for %s -  %s", str(time_series_start), str(time_series_end))
    
    pollution_df = _get_pollution_data(conn_id=conn_id, 
                    time_series_start=time_series_start, 
                    time_series_end=time_series_end
                    )
    
    df : np.ndarray = np.concatenate([weather_df, pollution_df], axis=1)
    path = f"model/models/{model_name}"

    model = RNNModel(input_size=22, hidden_size=128, output_size=1, num_layers=2)
    model.load_state_dict(torch.load(path, weights_only=True))
    model.eval()
    
    logger.info(type(df))
    df = torch.tensor(np.float32(df))
    
    predictions = _predict(prediction_len=24, model=model, df=df, weather_predictions=weather_prediction_df)
    
    df_predictions = pd.DataFrame(predictions, columns=["predictions"])
    
    df_predictions["time"] = weather_df["time"]
    df_predictions["run"] = (datetime.now() + timedelta(hours=1)).replace(minute=0, second=0, microsecond=0)
    
    df_predictions.set_index("run", inplace=True)
    
    _save_predictions(df_predictions)

    return 

def _get_weather_data(conn_id : str, time_series_start, time_series_end):
    return _get_data(conn_id, time_series_start, time_series_end, table="weather")

def _get_pollution_data(conn_id : str, time_series_start, time_series_end):
    return _get_data(conn_id, time_series_start, time_series_end, table="pollution")

def _get_weather_predictions_data(conn_id : str, time_series_start, time_series_end):
    return _get_data(conn_id, time_series_start, time_series_end, table="weather_predictions")

def _get_data(conn_id : str, time_series_start, time_series_end, table):
        
    if table == "pollution":
        cols = "pm10, pm2_5"
    else:
        cols = "*"
    
    logger.info("attempting data read table %s, columns %s", table, cols)
    
    if table == "weather_predictions":
        sql_query = f"""SELECT {cols} 
                    FROM {table}
                    WHERE run == '{(datetime.now() + timedelta(hours=1)).replace(minute=0, second=0, microsecond=0)}'
                    ORDER BY time"""
    else: 
        sql_query = f"""SELECT {cols} 
                    FROM {table}
                    WHERE time >= '{time_series_start}'
                    AND time < '{time_series_end}'
                    ORDER BY time"""
    
    with MyPostgresHook(conn_id=conn_id).get_conn() as conn:
        df : pd.DataFrame = pd.read_sql(
            sql=sql_query,
            con=conn)
             
    logger.info("fetched %i rows", df.shape[0])
    
    if table=="pollution":
        return df[["pm10", "pm2_5"]]
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
    