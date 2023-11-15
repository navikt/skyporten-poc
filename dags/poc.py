from airflow import DAG
from datetime import datetime
from dataverk_airflow import python_operator

with DAG(dag_id="skyporten_demo", schedule_interval=None, start_date=datetime(2023, 11, 14), catchup=False) as dag:
    t1 = python_operator(dag=dag,
                         name="demo",
                         requirements_path="/requirements.txt",
                         script_path="/main.py")

    t1
