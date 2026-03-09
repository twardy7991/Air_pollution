import torch
import pandas as pd
from datetime import datetime
from projects.Air_pollution.airflow_project.model.rnn_model import RNNModel
from plugins.my_postgres_hook import MyPostgresHook

def _recompute_predictions(timestamp_to_predict):
    
    torch.load()
    return

def _recompute_model_predictions(timestamp_to_predict, model_name : str, conn_id : str):
    
    timestamp_to_predict : datetime
    
    time_series_start = timestamp_to_predict - datetime.hour(24)
    time_series_end = timestamp_to_predict - datetime.hour(1)
    
    data = _get_data(conn_id=conn_id, 
                    time_series_start=time_series_start, 
                    time_series_end=time_series_end)
    
    model : RNNModel = torch.load(model_name)
    
    predictions = model(data)
    
    return

def _get_data(conn_id : str, time_series_start, time_series_end):
    
    with MyPostgresHook(conn_id=conn_id).get_conn() as conn:
        
        pd.read_sql(
            sql=f"""SELECT * 
                    FROM weather
                    WHERE timestamp >= {time_series_start}
                    AND timestamp < {time_series_end}
                    ORDER BY timestamp""",
            con=conn)
        
def _save_predictions(data : pd.DataFrame, conn_id):
    
    with MyPostgresHook(conn_id=conn_id).get_conn() as conn:
        
        data.to_sql(
            name="predictions",
            con=conn,
            if_exists="replace"
        )
    