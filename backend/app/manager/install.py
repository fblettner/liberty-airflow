import os
import subprocess
import sys

from app.utils.utils import load_env

def install_airflow():

    load_env()
    airflow_version = os.getenv("AIRFLOW_VERSION", "2.10.2")  
    python_version = os.getenv("PYTHON_VERSION", "3.12")  

    constraint_url = f"https://raw.githubusercontent.com/apache/airflow/constraints-{airflow_version}/constraints-{python_version}.txt"

    commands = [
        f'pip install "apache-airflow[postgres]=={airflow_version}" --constraint "{constraint_url}"',
        "pip install apache-airflow-providers-apache-spark pyspark apache-airflow-providers-oracle apache-airflow-providers-postgres"
    ]

    for cmd in commands:
        subprocess.run(cmd, shell=True, check=True)

    print("Airflow installed successfully.")
    subprocess.Popen("airflow db init", shell=True)

if __name__ == "__main__":
    install_airflow()