import os
import subprocess
from liberty.scheduler.utils.common import load_env

def stop_airflow():
    """Stops all Airflow services, including Celery workers."""
    load_env()  # Load .env file

    os.system("source .venv/bin/activate")

    print("🛑 Stopping Airflow Scheduler...")
    subprocess.run("pkill -f 'airflow scheduler'", shell=True)

    print("🛑 Stopping Airflow Dag Processor...")
    subprocess.run("pkill -f 'airflow dag-processor'", shell=True)

    print("🛑 Stopping Airflow API Server...")
    subprocess.run("pkill -f 'airflow api_server'", shell=True)
    
    print("✅ Airflow stopped successfully.")

if __name__ == "__main__":
    stop_airflow()