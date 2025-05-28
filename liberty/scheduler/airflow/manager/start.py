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
    
    print("🌍 Starting Airflow API Server...")
    subprocess.Popen("nohup airflow api-server > ./logs/api-server.log 2>&1 &", shell=True)

    print("🌍 Starting Airflow Dag Processor...")
    subprocess.Popen("nohup airflow dag-processor > ./logs/dag-processor.log 2>&1 &", shell=True)


if __name__ == "__main__":
    start_airflow()