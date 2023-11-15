from airflow import DAG
from datetime import datetime
from dataverk_airflow import python_operator
from airflow.models import Variable

with DAG(dag_id="skyporten_demo", schedule_interval=None, start_date=datetime(2023, 11, 14), catchup=False) as dag:
    t1 = python_operator(dag=dag,
                         name="demo",
                         repo="navikt/skyporten-poc",
                         requirements_path="/requirements.txt",
                         script_path="/main.py",
                         extra_vars={
                             "MASKINPORTEN_CLIENT_JWK": Variable.get("MASKINPORTEN_CLIENT_JWK"),
                             "MASKINPORTEN_CLIENT_ID": Variable.get("MASKINPORTEN_CLIENT_ID")
                         })

    t1
