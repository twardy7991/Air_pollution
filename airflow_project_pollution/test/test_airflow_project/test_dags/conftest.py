import json
from contextlib import contextmanager
from datetime import datetime

import pytest
import pandas as pd

from my_postgres_hook import MyPostgresHook

@pytest.fixture
def download_pollution_setup(request, monkeypatch, mocker, conn):
    data_type : str = request.param
    
    @contextmanager
    def mock_conn(*args):
        yield conn
    
    def mock_innit(*args, **kwargs):
        return
     
    monkeypatch.setattr(MyPostgresHook, "get_conn", mock_conn)
    monkeypatch.setattr(MyPostgresHook, "__init__", mock_innit)
    
    monkeypatch.setenv("LAST_DATE_STORED_POLLUTION", str(datetime(year=2023, month=1, day=1, hour=0)))
    monkeypatch.setenv("LAST_DATE_STORED_WEATHER", str(datetime(year=2023, month=1, day=1, hour=0)))
    
    class MockResponse:
        status_code = 200
        
        match data_type:
            case "pollution":
                text = json.dumps({
                    "hourly" : {
                        "time" : [str(datetime(year=2023, month=1, day=1, hour=0)), 
                                str(datetime(year=2023, month=1, day=1, hour=1)), 
                                str(datetime(year=2023, month=1, day=1, hour=2)),
                                str(datetime(year=2023, month=1, day=1, hour=3))],
                        "pm2_5" : [10, 20, 30, 20],
                        "pm10" : [10, 10, 50, 20],
                    }
                })
            case "weather":
                text = json.dumps({
                    "hourly": {
                        "time": [str(datetime(year=2023, month=1, day=1, hour=0)), 
                                str(datetime(year=2023, month=1, day=1, hour=1)), 
                                str(datetime(year=2023, month=1, day=1, hour=2)),
                                str(datetime(year=2023, month=1, day=1, hour=3))],
                        "temperature_2m": [5, 6, 7, 6],
                        "relative_humidity_2m": [80, 78, 75, 82],
                        "dew_point_2m": [2, 3, 4, 3],
                        "apparent_temperature": [4, 5, 6, 5],
                        "pressure_msl": [1015, 1016, 1014, 1013],
                        "surface_pressure": [1005, 1006, 1004, 1003],

                        "cloud_cover": [60, 50, 40, 70],
                        "cloud_cover_low": [20, 10, 5, 30],
                        "cloud_cover_mid": [25, 30, 20, 25],
                        "cloud_cover_high": [15, 10, 15, 15],

                        "wind_speed_10m": [10, 12, 8, 7],
                        "wind_speed_80m": [15, 17, 13, 12],
                        "wind_speed_120m": [18, 20, 15, 14],
                        "wind_speed_180m": [20, 22, 17, 16],

                        "wind_direction_10m": [180, 190, 200, 210],
                        "wind_direction_80m": [185, 195, 205, 215],
                        "wind_direction_120m": [190, 200, 210, 220],
                        "wind_direction_180m": [195, 205, 215, 225],

                        "wind_gusts_10m": [25, 30, 20, 18],

                        "shortwave_radiation": [0, 50, 120, 80],
                        "direct_radiation": [0, 40, 100, 70],
                        "direct_normal_irradiance": [0, 60, 150, 90],
                        "diffuse_radiation": [0, 10, 20, 10],
                        "global_tilted_irradiance": [0, 55, 130, 85],

                        "vapour_pressure_deficit": [1, 2, 3, 2],
                        "cape": [0, 50, 100, 20],

                        "evapotranspiration": [0, 1, 2, 1],
                        "et0_fao_evapotranspiration": [0, 1, 2, 1],

                        "precipitation": [0, 0, 1, 0],
                        "snowfall": [0, 0, 0, 0],
                        "precipitation_probability": [10, 20, 60, 30],
                        "rain": [0, 0, 1, 0],
                        "showers": [0, 0, 1, 0],

                        "weather_code": [1, 2, 3, 2],

                        "snow_depth": [0, 0, 0, 0],
                        "freezing_level_height": [1500, 1400, 1300, 1450],
                        "visibility": [10000, 9000, 8000, 9500],

                        "soil_temperature_0cm": [4, 5, 6, 5],
                        "soil_temperature_6cm": [5, 6, 7, 6],
                        "soil_temperature_18cm": [6, 7, 8, 7],
                        "soil_temperature_54cm": [7, 8, 9, 8],

                        "soil_moisture_0_to_1cm": [30, 32, 31, 29],
                        "soil_moisture_1_to_3cm": [35, 36, 34, 33],
                        "soil_moisture_3_to_9cm": [40, 42, 41, 39],
                        "soil_moisture_9_to_27cm": [45, 47, 46, 44],
                        "soil_moisture_27_to_81cm": [50, 52, 51, 49],

                        "is_day": [0, 1, 1, 0]
                    }
                })
            
    monkeypatch.setattr("requests.get", lambda *args, **kwargs: MockResponse)
    
    match data_type: 
        case "pollution":
            expected_pollution_data = pd.DataFrame(data=[
            [str(datetime(year=2023, month=1, day=1, hour=1)), 20, 10],
            [str(datetime(year=2023, month=1, day=1, hour=2)), 30, 50],
            ]   , columns=["time", "pm2_5", "pm10"])
        
            expected_pollution_data["time"] = expected_pollution_data["time"].astype('datetime64[s]')
            expected_pollution_data["pm2_5"] = expected_pollution_data["pm2_5"].astype('int64')
            expected_pollution_data["pm10"] = expected_pollution_data["pm10"].astype('int64')
            
            expected_prediction_data = pd.DataFrame(data=[
            [str(datetime(year=2023, month=1, day=1, hour=3)), 20, 20],
            ]   , columns=["time", "pm2_5", "pm10"])
        
            expected_prediction_data["time"] = expected_prediction_data["time"].astype('datetime64[s]')
            expected_prediction_data["pm2_5"] = expected_prediction_data["pm2_5"].astype('int64')
            expected_prediction_data["pm10"] = expected_prediction_data["pm10"].astype('int64')
            
            expected_data = (expected_pollution_data, expected_prediction_data, data_type)
            
        case "weather":    
            expected_weather_data = pd.DataFrame(data=[
                [
                    str(datetime(2023, 1, 1, 1)), 6, 78, 3, 5, 1016, 1006,
                    50, 10, 30, 10,
                    12, 17, 20, 22,
                    190, 195, 200, 205,
                    30,
                    50, 40, 60, 10, 55,
                    2, 50,
                    1, 1,
                    0, 0, 20, 0, 0,
                    2,
                    0, 1400, 9000,
                    5, 6, 7, 8,
                    32, 36, 42, 47, 52,
                    1
                ],
                [
                    str(datetime(2023, 1, 1, 2)), 7, 75, 4, 6, 1014, 1004,
                    40, 5, 20, 15,
                    8, 13, 15, 17,
                    200, 205, 210, 215,
                    20,
                    120, 100, 150, 20, 130,
                    3, 100,
                    2, 2,
                    1, 0, 60, 1, 1,
                    3,
                    0, 1300, 8000,
                    6, 7, 8, 9,
                    31, 34, 41, 46, 51,
                    1
                ]
            ], columns=[
                "time",
                "temperature_2m", "relative_humidity_2m", "dew_point_2m",
                "apparent_temperature", "pressure_msl", "surface_pressure",
                "cloud_cover", "cloud_cover_low", "cloud_cover_mid", "cloud_cover_high",
                "wind_speed_10m", "wind_speed_80m", "wind_speed_120m", "wind_speed_180m",
                "wind_direction_10m", "wind_direction_80m", "wind_direction_120m", "wind_direction_180m",
                "wind_gusts_10m",
                "shortwave_radiation", "direct_radiation", "direct_normal_irradiance",
                "diffuse_radiation", "global_tilted_irradiance",
                "vapour_pressure_deficit", "cape",
                "evapotranspiration", "et0_fao_evapotranspiration",
                "precipitation", "snowfall", "precipitation_probability",
                "rain", "showers",
                "weather_code",
                "snow_depth", "freezing_level_height", "visibility",
                "soil_temperature_0cm", "soil_temperature_6cm",
                "soil_temperature_18cm", "soil_temperature_54cm",
                "soil_moisture_0_to_1cm", "soil_moisture_1_to_3cm",
                "soil_moisture_3_to_9cm", "soil_moisture_9_to_27cm",
                "soil_moisture_27_to_81cm",
                "is_day"
            ])

            expected_weather_data["time"] = expected_weather_data["time"].astype("datetime64[s]")
            #expected_weather_data = expected_weather_data.astype("int64", errors="ignore")

            expected_weather_prediction_data = pd.DataFrame(data=[[
                str(datetime(2023, 1, 1, 3)), 
                6, 82, 3, 5, 1013, 1003,
                70, 30, 25, 15,
                7, 12, 14, 16,
                210, 215, 220, 225,
                18,
                80, 70, 90, 10, 85,
                2, 20,
                1, 1,
                0, 0, 30, 0, 0,
                2,
                0, 1450, 9500,
                5, 6, 7, 8,
                29, 33, 39, 44, 49,
                0
            ]], columns=expected_weather_data.columns)

            expected_weather_prediction_data["time"] = expected_weather_prediction_data["time"].astype("datetime64[s]")
            #expected_weather_prediction_data = expected_weather_prediction_data.astype("int64", errors="ignore")

            expected_data = (expected_weather_data, expected_weather_prediction_data, data_type)

    yield expected_data