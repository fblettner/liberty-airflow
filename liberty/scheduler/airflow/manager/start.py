import os
import subprocess
from liberty.scheduler.utils.common import load_env

def start_airflow():
    """Start Airflow with CeleryExecutor (Scheduler, Webserver, Workers)."""
    load_env()  # Load .env file

    airflow_home = os.getenv("AIRFLOW_HOME", os.getcwd())  # Default to current directory
    os.environ["AIRFLOW_HOME"] = airflow_home

    print("🚀 Starting Airflow Scheduler...")
    subprocess.Popen("nohup airflow scheduler > ./logs/scheduler.log 2>&1 &", shell=True)
    
    print("🌍 Starting Airflow Webserver...")
    subprocess.Popen("nohup airflow webserver > ./logs/webserver.log 2>&1 &", shell=True)
    

if __name__ == "__main__":
    start_airflow()