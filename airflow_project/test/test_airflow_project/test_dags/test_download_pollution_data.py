import pandas as pd
from my_postgres_hook import MyPostgresHook
from pandas.testing import assert_frame_equal
from contextlib import contextmanager
from download_data import _save_to_database, _download_data
from datetime import datetime
import json


import pytest

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

def test_download_pollution_data(monkeypatch, mocker, conn):
    
    @contextmanager
    def mock_conn(*args):
        yield conn
    
    def mock_innit(*args, **kwargs):
        return
    
    monkeypatch.setattr(MyPostgresHook, "get_conn", mock_conn)
    monkeypatch.setattr(MyPostgresHook, "__init__", mock_innit)
    
    class MockResponse:
        status_code = 200
        text = json.dumps({
            "hourly" : {
                "time" : [str(datetime(year=2023, month=1, day=1)), 
                          str(datetime(year=2023, month=1, day=2)), 
                          str(datetime(year=2023, month=1, day=3))],
                "pm2_5" : [10, 20, 30]
            }
        })
    
    monkeypatch.setenv("LAST_DATE_STORED_POLLUTION", str(datetime(year=2023, month=1, day=1)))
    monkeypatch.setattr("requests.get", lambda *args, **kwargs: MockResponse)
    #monkeypatch.setattr("datetime.date", str(datetime(year=2023, month=1, day=3)))
    #monkeypatch.setattr("datetime.time", "00:00")
    
    save_to_database_patched = mocker.patch("download_data._save_to_database")
    
    _download_data(data_type="pollution", 
                             current_date=datetime(year=2023, month=1, day=3), 
                             conn_id="")
    
    expected_data = pd.DataFrame(data=[
        [str(datetime(year=2023, month=1, day=2)), 20],
        [str(datetime(year=2023, month=1, day=3)), 30]
        ], columns=["time", "pm2_5"])
    
    expected_data["time"] = expected_data["time"].astype('datetime64[s]')
    expected_data["pm2_5"] = expected_data["pm2_5"].astype('int64')
    
    called_data : pd.DataFrame = save_to_database_patched.call_args.kwargs["data"]
    called_data = called_data.reset_index(drop=True)
    
    print(called_data)
    print(expected_data)
    print(called_data.dtypes)
    print(expected_data.dtypes)
    
    assert_frame_equal(called_data, expected_data)
    
    # saved_data = pd.read_sql(sql="""
    #     SELECT time, pm2_5
    #     FROM pollution
    #     ORDER BY time ASC""",
    #     con=conn)

from download_data import ForecastNotAvailable

def test_download_data_wrong_status_code(monkeypatch):
    
    with pytest.raises(ForecastNotAvailable):
        class MockResponse:
            status_code = 504
            reason = "request timeout"

        monkeypatch.setenv("LAST_DATE_STORED_POLLUTION", str(datetime(year=2023, month=1, day=1)))
        monkeypatch.setattr("requests.get", lambda *args, **kwargs: MockResponse)

        _download_data(data_type="pollution", 
                                current_date=datetime(year=2023, month=1, day=3))
    
    
    