import os
import subprocess
from app.utils.utils import load_env

def stop_airflow():
    load_env()  # Load .env file

    os.system("source .venv/bin/activate")
    
    print("Stopping Airflow processes...")
    subprocess.run("pkill -f 'airflow scheduler'", shell=True)
    subprocess.run("pkill -f 'airflow webserver'", shell=True)

    print("Airflow stopped successfully.")

if __name__ == "__main__":
    stop_airflow()