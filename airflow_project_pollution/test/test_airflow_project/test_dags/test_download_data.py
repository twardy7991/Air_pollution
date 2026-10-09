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
        ["2026-03-12 15:30:00", 10, 10],
        ["2026-03-12 16:30:00", 20, 10],
        ["2026-03-12 17:30:00", 30, 10],
        ["2026-03-12 18:30:00", 40, 10],
    ],
    columns=["time", "pm2_5", "pm10"]
    )
    
    data_to_save["time"] = data_to_save["time"].astype("datetime64[ns]")

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

@pytest.mark.parametrize("download_pollution_setup", [("pollution"), ("weather")], indirect=True)
def test_download_data(download_pollution_setup, monkeypatch, mocker):

    expected_historic_data, expected_prediction_data, data_type = download_pollution_setup
    
    save_to_database_patched = mocker.patch("download_data._save_to_database")
    
    _download_data(data_type=data_type, 
                            current_date=datetime(year=2023, month=1, day=1, hour=2), 
                            conn_id="")
    
    called_historic_data : pd.DataFrame = save_to_database_patched.call_args_list[0].kwargs["data"]
    called_predictions_data : pd.DataFrame = save_to_database_patched.call_args_list[1].kwargs["data"]

    called_historic_data = called_historic_data.reset_index(drop=True)
    called_predictions_data = called_predictions_data.reset_index(drop=True)
    
    print(called_historic_data)
    print(expected_historic_data)
    
    assert_frame_equal(called_historic_data, expected_historic_data)
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