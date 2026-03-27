import requests
from datetime import datetime, timedelta
import os
import json
import pandas as pd
from my_postgres_hook import MyPostgresHook
import logging

from constants import _get_params, BASE_URL_FORECAST, BASE_URL_POLLUTION
from typing import Literal

class ForecastNotAvailable(BaseException):
    def __init__(self,*args):
        super().__init__(*args)

logger = logging.getLogger(__name__)
logger.setLevel("INFO")

def _download_data(data_type : Literal["pollution", "weather"], current_date : datetime, lat : int = 50.05, lon : int = 19.92, conn_id : str = "POSTGRES_CONN_POLLUTION", prediction_threshold : int = 24):

    match data_type:
        case "pollution":
            url = BASE_URL_POLLUTION
            env_date = "LAST_DATE_STORED_POLLUTION"
            
        case "weather": 
            url = BASE_URL_FORECAST
            env_date = "LAST_DATE_STORED_WEATHER"

    last_date = datetime.fromisoformat(os.getenv(env_date))
    diff_date = current_date - last_date
    days = 1#diff_date.days
    
    params = _get_params(data_type=data_type, lon=lon, lat=lat, days=days)     
    logger.info("attempting a request url: %s,\nparams %s", url, params)
    response = requests.get(url=url, params=params)
    
    if response.status_code != 200:
        raise ForecastNotAvailable(f"Error while fetching data \nstatus code: {response.status_code}\n{response.reason}")
    
    df = pd.DataFrame(json.loads(response.text)["hourly"])
    df["time"] = df["time"].astype('datetime64[s]')
    df_historic = df[(df["time"] > last_date) & (df["time"] <= current_date)]

    match data_type:
        case "pollution":
            df_predictions = df[df["time"] > current_date]
            _save_to_database(data_type="pollution" ,data=df_historic, conn_id=conn_id)
            _save_to_database(data_type="official_pollution_predictions" ,data=df_predictions, conn_id=conn_id)
        case "weather":
            df_predictions = df[df["time"] > current_date]
            _save_to_database(data_type="weather" ,data=df_historic, conn_id=conn_id)
            _save_to_database(data_type="official_weather_predictions" ,data=df_predictions, conn_id=conn_id)
            
    os.environ[env_date] = current_date.isoformat()
    
    return 0
    
def _save_to_database(data_type : Literal["pollution", "weather", "official_pollution_predictions", "official_weather_predictions"], data : pd.DataFrame, conn_id : str):
    
    if data_type == "official_weather_predictions" or data_type == "official_pollution_predictions":
        data["run"] = (datetime.now() + timedelta(hours=1)).replace(minute=0, second=0, microsecond=0)
    
    #hook manages the transaction itself
    with MyPostgresHook(conn_id=conn_id).get_conn() as connection:
        
        # we give pandas connection with open transaction, so that it does not commit automatically
        data.to_sql(
            name=data_type,
            con = connection,
            if_exists="append",
            index=False
        )
    
    return