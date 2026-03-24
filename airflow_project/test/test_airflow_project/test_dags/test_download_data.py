import json
from contextlib import contextmanager
from datetime import datetime

import pytest
import pandas as pd
from pandas.testing import assert_frame_equal

from my_postgres_hook import MyPostgresHook
from download_data import _save_to_database, _download_data
from download_data import ForecastNotAvailable

def test_save_to_database(monkeypatch, conn):
    
    data_to_save = pd.DataFrame([
        ["2026-03-12T15:30:00+01:00", 10, 10],
        ["2026-03-12T16:30:00+01:00", 20, 10],
        ["2026-03-12T17:30:00+01:00", 30, 10],
        ["2026-03-12T18:30:00+01:00", 40, 10],
    ],
    columns=["time", "pm2_5", "pm10"]
    )

    @contextmanager
    def mock_conn(*args):
        yield conn
    
    def mock_innit(*args, **kwargs):
        return
    
    monkeypatch.setattr(MyPostgresHook, "get_conn", mock_conn)
    monkeypatch.setattr(MyPostgresHook, "__init__", mock_innit)
    
    _save_to_database(data_type="pollution" ,data=data_to_save, conn_id="")
    
    saved_data = pd.read_sql(sql="""
            SELECT time, pm2_5, pm10
            FROM pollution
            ORDER BY time ASC""",
            con=conn)
    
    assert_frame_equal(data_to_save, saved_data)

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
    
    monkeypatch.setenv("LAST_DATE_STORED_POLLUTION", str(datetime(year=2023, month=1, day=1)))
    monkeypatch.setenv("LAST_DATE_STORED_WEATHER", str(datetime(year=2023, month=1, day=1)))
    
    class MockResponse:
        status_code = 200
        
        match data_type:
            case "pollution":
                text = json.dumps({
                    "hourly" : {
                        "time" : [str(datetime(year=2023, month=1, day=1)), 
                                str(datetime(year=2023, month=1, day=2)), 
                                str(datetime(year=2023, month=1, day=3)),
                                str(datetime(year=2023, month=1, day=4))],
                        "pm2_5" : [10, 20, 30, 20]
                    }
                })
            case "weather":
                text = json.dumps({
                    "hourly" : {
                        "time" : [str(datetime(year=2023, month=1, day=1)), 
                                str(datetime(year=2023, month=1, day=2)), 
                                str(datetime(year=2023, month=1, day=3))],
                        "pm2_5" : [10, 20, 30]
                    }
                })
    
    monkeypatch.setattr("requests.get", lambda *args, **kwargs: MockResponse)
    
    match data_type: 
        case "pollution":
            expected_pollution_data = pd.DataFrame(data=[
            [str(datetime(year=2023, month=1, day=2)), 20],
            [str(datetime(year=2023, month=1, day=3)), 30]
            ]   , columns=["time", "pm2_5"])
        
            expected_pollution_data["time"] = expected_pollution_data["time"].astype('datetime64[s]')
            expected_pollution_data["pm2_5"] = expected_pollution_data["pm2_5"].astype('int64')
            
            expected_prediction_data = pd.DataFrame(data=[
            [str(datetime(year=2023, month=1, day=4)), 20],
            ]   , columns=["time", "pm2_5"])
        
            expected_prediction_data["time"] = expected_prediction_data["time"].astype('datetime64[s]')
            expected_prediction_data["pm2_5"] = expected_prediction_data["pm2_5"].astype('int64')
            
            expected_data = (expected_pollution_data, expected_prediction_data)
        case "weather":
            expected_data = ""
            
    yield expected_data

@pytest.mark.parametrize("download_pollution_setup", [("pollution")], indirect=True)
def test_download_pollution_data(download_pollution_setup, monkeypatch, mocker):

    expected_pollution_data, expected_prediction_data = download_pollution_setup
    
    save_to_database_patched = mocker.patch("download_data._save_to_database")
    
    _download_data(data_type="pollution", 
                             current_date=datetime(year=2023, month=1, day=3), 
                             conn_id="")
    
    called_pollution_data : pd.DataFrame = save_to_database_patched.call_args_list[0].kwargs["data"]
    called_predictions_data : pd.DataFrame = save_to_database_patched.call_args_list[1].kwargs["data"]

    called_pollution_data = called_pollution_data.reset_index(drop=True)
    called_predictions_data = called_predictions_data.reset_index(drop=True)
    
    assert_frame_equal(called_pollution_data, expected_pollution_data)
    assert_frame_equal(called_predictions_data, expected_prediction_data)

def test_download_data_wrong_status_code(monkeypatch):
    
    with pytest.raises(ForecastNotAvailable):
        class MockResponse:
            status_code = 504
            reason = "request timeout"

        monkeypatch.setenv("LAST_DATE_STORED_POLLUTION", str(datetime(year=2023, month=1, day=1)))
        monkeypatch.setattr("requests.get", lambda *args, **kwargs: MockResponse)

        _download_data(data_type="pollution", 
                                current_date=datetime(year=2023, month=1, day=3))
    
    


    
    # saved_data = pd.read_sql(sql="""
    #     SELECT time, pm2_5
    #     FROM pollution
    #     ORDER BY time ASC""",
    #     con=conn)