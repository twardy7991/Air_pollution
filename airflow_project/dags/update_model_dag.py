from airflow import DAG
import airflow
from datetime import datetime
from airflow.operators.python import PythonOperator
from dags.download_weather_data import _download_weather_data
from dags.download_pollution_data import _download_pollution_data
from dags.recompute_predictions import _recompute_predictions

update_model_dag = DAG(
    dag_id="download_model",
    start_date=datetime(year=2026, month=3, day=7),
    # schedule_interval=
)

download_weather_data = PythonOperator(
    task_id = "download_weather",
    python_callable=_download_weather_data,
    dag=update_model_dag
)

download_pollution_data = PythonOperator(
    task_id = "download_pollution",
    python_callable=_download_pollution_data,
    dag=update_model_dag
)

recompute_predictions = PythonOperator(
    task_id="recompute_predictions",
    python_callable=_recompute_predictions,
    dag=update_model_dag
)

[download_pollution_data, download_weather_data] >> recompute_predictions


    





