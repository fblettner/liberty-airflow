from airflow.utils.db import provide_session
from airflow.jobs.job import Job
from airflow.models import DagRun, TaskInstance, Log
from airflow.models import Variable
import pendulum
import time
import os

# Get airflow retention days from Airflow variable
airflow_retention_days = int(Variable.get("airflow_retention_days", default_var=30))
retention_date = pendulum.now('UTC').subtract(days=airflow_retention_days)

@provide_session
def dag_runs(session=None):
    # Purge old DAG runs
    old_dag_runs = session.query(DagRun).filter(DagRun.execution_date < retention_date)
    old_dag_runs.delete(synchronize_session=False)
    session.commit()

@provide_session
def task_instances(session=None):
    # Purge old task instances
    old_task_instances = session.query(TaskInstance).filter(
        TaskInstance.execution_date < retention_date
    )
    old_task_instances.delete(synchronize_session=False)
    session.commit()

@provide_session
def jobs(session=None):
    # Purge old jobs
    old_jobs = session.query(Job).filter(Job.end_date < retention_date)
    old_jobs.delete(synchronize_session=False)
    session.commit()

@provide_session
def logs_in_db(session=None):
    # Purge old log records from the database
    old_logs = session.query(Log).filter(Log.dttm < retention_date)
    old_logs.delete(synchronize_session=False)
    session.commit()

airflow_home = os.getenv("AIRFLOW_HOME", os.getcwd())
LOG_DIR = os.path.join(airflow_home, "logs")

def logs_on_disk():
    now = time.time()
    cutoff = now - (airflow_retention_days * 86400)  # Convert days to seconds
    
    # Walk through the log directory and delete files older than the retention period
    for root, dirs, files in os.walk(LOG_DIR):
        for filename in files:
            file_path = os.path.join(root, filename)
            if os.path.isfile(file_path):
                file_modified_time = os.path.getmtime(file_path)
                if file_modified_time < cutoff:
                    print(f"Deleting log file: {file_path}")
                    os.remove(file_path)

