import requests
import json
import os
from datetime import datetime

import pandas as pd
from sqlalchemy.orm import Session

from models import Weather
from plugins.my_postgres_hook import MyPostgresHook

class ForecastNotAvailable(BaseException):
    def __init__(self,*args):
        super().__init__(*args)

BASE_URL_FORECAST = url = "https://api.open-meteo.com/v1/forecast"

def _download_weather_data(current_date : datetime, lat : int = 50.05, lon : int = 19.92, conn_id : str = "POSTGRES_CONN_POLLUTION") -> int:
    
    last_date = datetime.fromisoformat(os.getenv("LAST_DATE_STORED"))
    diff_date = current_date - last_date
    
    days = diff_date.days
     
    params={
        "latitude" : lat,
        "longitude" : lon,
        "forecast_days" : 1, 
        "past_days" : days,
        "hourly": ["temperature_2m", 
                   "relative_humidity_2m",
                   "dew_point_2m",
                   "apparent_temperature",
                   "pressure_msl",
                   "surface_pressure",
                   "cloud_cover",
                   "cloud_cover_low",
                   "cloud_cover_mid",
                   "cloud_cover_high",
                   "wind_speed_10m",
                   "wind_speed_80m",
                   "wind_speed_120m",
                   "wind_speed_180m",
                   "wind_direction_10m",
                   "wind_direction_80m",
                   "wind_direction_120m",
                   "wind_direction_180m",
                   "wind_gusts_10m",
                   "shortwave_radiation",
                   "direct_radiation",
                   "direct_normal_irradiance",
                   "diffuse_radiation",
                   "global_tilted_irradiance",
                   "vapour_pressure_deficit",
                   "cape",
                   "evapotranspiration",
                   "et0_fao_evapotranspiration",
                   "precipitation",
                   "snowfall",
                   "precipitation_probability",
                   "rain",
                   "showers",
                   "weather_code",
                   "snow_depth",
                   "freezing_level_height",
                   "visibility",
                   "soil_temperature_0cm",
                   "soil_temperature_6cm",
                   "soil_temperature_18cm",
                   "soil_temperature_54cm",
                   "soil_moisture_0_to_1cm",
                   "soil_moisture_1_to_3cm",
                   "soil_moisture_3_to_9cm",
                   "soil_moisture_9_to_27cm",
                   "soil_moisture_27_to_81cm",
                   "is_day",
                   ],        
    }             

    response = requests.get(url=BASE_URL_FORECAST, params=params)
    
    if response.status_code != 200:
        raise ForecastNotAvailable(f"Error while fetching data \nstatus code: {response.status_code}\n{response.reason}")
    
    df = pd.DataFrame(json.loads(response.text["hourly"]))
    
    df = df[(df["time"] > last_date) & (df["time"] <= current_date)]
    
    _save_to_database(data=df, conn_id=conn_id)
    
    os.environ["LAST_DATE_STORED"] = current_date.isoformat()
    
    return 0

def _save_to_database(data : pd.DataFrame, conn_id : str) -> int:
    
    with MyPostgresHook(conn_id=conn_id).get_conn() as connection:
        
        data.to_sql(
            name="weather",
            conn = connection,
            if_exists="replace"
        )
        
    # with Session(MyPostgresHook(conn_id=conn_id).engine) as session:
    #     with session.begin():
            
    #         weather_data = [Weather(entry[k] for k in fields) for entry in data]
            
    #         session.bulk_save_objects(weather_data)
            
    #         session.commit()
    
    return 0
        
    
