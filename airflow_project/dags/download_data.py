import requests
from datetime import datetime
import os
import json
import pandas as pd
from my_postgres_hook import MyPostgresHook

class ForecastNotAvailable(BaseException):
    def __init__(self,*args):
        super().__init__(*args)

from constants import _get_params, BASE_URL_FORECAST, BASE_URL_POLLUTION
from typing import Literal

def _download_data(data_type : Literal["pollution", "weather"], current_date : datetime, lat : int = 50.05, lon : int = 19.92, conn_id : str = "POSTGRES_CONN_POLLUTION"):

    if data_type == "pollution":
        url = BASE_URL_POLLUTION
        env_date = "LAST_DATE_STORED_POLLUTION"
    else: 
        url = BASE_URL_FORECAST
        env_date = "LAST_DATE_STORED_WEATHER"
    
    last_date = datetime.fromisoformat(os.getenv(env_date))
    diff_date = current_date - last_date
    days = diff_date.days

    response = requests.get(url=url, params=_get_params(data_type=data_type, lon=lon, lat=lat, days=days))
        
    if response.status_code != 200:
        raise ForecastNotAvailable(f"Error while fetching data \nstatus code: {response.status_code}\n{response.reason}")
    
    df = pd.DataFrame(json.loads(response.text)["hourly"])

    df["time"] = df["time"].astype('datetime64[s]')
    df = df[(df["time"] > last_date) & (df["time"] <= current_date)]
    
    _save_to_database(data_type=data_type ,data=df, conn_id=conn_id)
    
    os.environ[env_date] = current_date.isoformat()
    
    return 0
    
def _save_to_database(data_type : Literal["pollution", "weather"], data : pd.DataFrame, conn_id : str):
    
    #hook manages the transaction itself
    with MyPostgresHook(conn_id=conn_id).get_conn() as connection:
        
        # we give pandas connection with open transaction, so that it does not commit automatically
        data.to_sql(
            name=data_type,
            con = connection,
            if_exists="replace"
        )
        
        print("data_added")
        #logger.info("")
    
    # with Session(MyPostgresHook(conn_id=conn_id).engine) as session:
    #     with session.begin():
            
    #         weather_data = [Weather(entry[k] for k in fields) for entry in data]
            
    #         session.bulk_save_objects(weather_data)
            
    #         session.commit()
        
    return