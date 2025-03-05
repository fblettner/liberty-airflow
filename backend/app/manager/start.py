import os
import subprocess
from app.utils.utils import load_env

def start_airflow():
    load_env()  # Load .env file

    print("Starting Airflow Scheduler...")
    subprocess.Popen("nohup airflow scheduler > ./logs/scheduler.log 2>&1 &", shell=True)
    
    print("Starting Airflow Webserver...")
    subprocess.Popen("nohup airflow webserver > ./logs/webserver.log 2>&1 &", shell=True)

    print("Airflow services started successfully.")

if __name__ == "__main__":
    start_airflow()