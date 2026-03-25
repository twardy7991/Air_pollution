from airflow import DAG
import airflow
from datetime import datetime
from airflow.providers.standard.operators.python import PythonOperator
from download_data import _download_data
from recompute_predictions import _recompute_model_predictions

update_model_dag = DAG(
    dag_id="update_model",
    #start_date=datetime(year=2026, month=3, day=26, hour=1),
    #catchup=False
    # schedule_interval=
)

download_weather_data = PythonOperator(
    task_id = "download_weather",
    python_callable=_download_data,
    op_kwargs={
        "data_type" : "weather",
        "current_date" : datetime.now(),
        "lat" : 50.05,
        "lon" : 19.92,
        "conn_id" : "POSTGRES_CONN_POLLUTION",
        "prediction_threshold" : 24
    },
    dag=update_model_dag
)

download_pollution_data = PythonOperator(
    task_id = "download_pollution",
    python_callable=_download_data,
    op_kwargs={
        "data_type" : "pollution",
        "current_date" : datetime.now(),
        "lat" : 50.05,
        "lon" : 19.92,
        "conn_id" : "POSTGRES_CONN_POLLUTION",
        "prediction_threshold" : 24
    },
    dag=update_model_dag
)

recompute_predictions = PythonOperator(
    task_id="recompute_predictions",
    python_callable=_recompute_model_predictions,
    op_kwargs={
        "timestamp_to_predict" :  datetime.now(),
        "model_name" : "model_1.pt",
        "conn_id" : "POSTGRES_CONN_POLLUTION"
    },
    dag=update_model_dag
)

[download_pollution_data, download_weather_data] >> recompute_predictions





