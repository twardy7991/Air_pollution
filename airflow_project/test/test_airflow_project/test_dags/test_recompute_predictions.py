import pandas as pd
from datetime import datetime
from contextlib import contextmanager

from recompute_predictions import _save_predictions, _recompute_model_predictions
from pandas.testing import assert_frame_equal
    
from recompute_predictions import _get_data

def test_save_predictions(conn, monkeypatch):
    
    data_to_save = pd.DataFrame(data=[
        ["run1", datetime(year=2023, month=1, day=1), 10],
        ["run1", datetime(year=2023, month=1, day=2), 20]
    ], columns=["run", "time", "pm2_5"])

    @contextmanager
    def mock_conn(*args, **kwargs):
        yield conn
    
    monkeypatch.setattr("my_postgres_hook.MyPostgresHook.get_conn", mock_conn)
    monkeypatch.setattr("my_postgres_hook.MyPostgresHook.__init__", lambda *args, **kwargs: None)
    
    _save_predictions(data=data_to_save, conn_id="") 
    
    saved_data = pd.read_sql(sql="""
        SELECT run, time, pm2_5
        FROM predictions
        """,
        con=conn)
    
    print(saved_data)
    
    assert_frame_equal(data_to_save, saved_data)
    
from unittest.mock import MagicMock

def test_get_pollution_data(monkeypatch, conn):
    
    @contextmanager
    def mock_conn(*args, **kwargs):
        yield conn
    
    monkeypatch.setattr("my_postgres_hook.MyPostgresHook.get_conn", mock_conn)
    monkeypatch.setattr("my_postgres_hook.MyPostgresHook.__init__", lambda *args, **kwargs: None)
    
    data_in_db : pd.DataFrame = pd.DataFrame(data=[
        [datetime(year=2023, month=1, day=1), 10, 1],
        [datetime(year=2023, month=1, day=2), 20, 2],
        [datetime(year=2023, month=1, day=3), 30, 3],
    ], columns=["time", "pm2_5", "pm_10"])
    
    data_in_db.to_sql(name="pollution", con=conn, if_exists="append", index=False)
    
    time_series_start = datetime(year=2023, month=1, day=1)
    time_series_end = datetime(year=2023, month=1, day=3)
    
    readed_data : pd.DataFrame = _get_data(conn_id="", 
                                           time_series_start=time_series_start, 
                                           time_series_end=time_series_end,
                                           table="pollution")
    
    expected_data = pd.DataFrame(data=[
        [10],
        [20],
    ], columns=["pm2_5"])
    
    assert_frame_equal(expected_data, readed_data)
    
from unittest import mock
import numpy as np

def test_recompute_model_predictions(conn, monkeypatch, mocker : mock):
    
    predictions = np.array(
        [[1],
        [2]]
    )
    
    def patched_torch_load(*args, **kwargs):
        def foo(*args, **kwargs):
            return predictions
        return foo    
    
    monkeypatch.setattr("torch.load", patched_torch_load)
    
    save_prediction_patched : MagicMock = mocker.patch("recompute_predictions._save_predictions")
    
    patched_get_weather = mocker.patch("recompute_predictions._get_weather_data")
    patched_get_weather.return_value = pd.DataFrame(data=[
        [0],
        [1]
    ], columns=["time"])
    
    patched_get_pollution = mocker.patch("recompute_predictions._get_pollution_data")
    patched_get_pollution.return_value = pd.DataFrame(data=[[0], [1]])
    
    class PatchedDateTime:
        @classmethod
        def now(cls):
            return datetime(2023, 10, 10, 10)
        
    monkeypatch.setattr(
        "recompute_predictions.datetime",
        PatchedDateTime
    )
    
    _recompute_model_predictions(timestamp_to_predict=datetime.now(), model_name="", conn_id="")
    
    expected_saved_predictions_df = pd.DataFrame(
        data = [
            [1, 0],
            [2, 1]
        ], 
        columns=["predictions", "time"],
        index=pd.Index(['run_2023-10-10_10:00:00', 'run_2023-10-10_10:00:00'], name='run')
    )
    
    saved_predictions = save_prediction_patched.call_args.args[0]
    
    assert_frame_equal(expected_saved_predictions_df, saved_predictions)
    
    
    