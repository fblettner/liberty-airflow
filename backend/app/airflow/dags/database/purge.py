from airflow import DAG
from airflow.models import Variable
from airflow.operators.python import PythonOperator
from airflow.utils.dates import days_ago
from app.airflow.plugins.git.utils import purge_old_backups
import logging

def purge_db_dag(dag_id, schedule, default_args):
    """
    Creates a DAG to purge old database backup.
    
    :param dag_id: ID of the DAG
    :param schedule: Schedule interval of the DAG
    :param default_args: Default arguments for the DAG
    :return: DAG object
    """

    # Get backup retention days from Airflow variable
    backup_retention_days = int(Variable.get("backup_retention_days", default_var=30))
    backup_directory = Variable.get("backup_directory", default_var=30)
    backup_repository = Variable.get("backup_repository", default_var=30)

    dag = DAG(
        dag_id=dag_id,
        default_args=default_args,
        description=f'Purge backup files older than {backup_retention_days} days from Git',
        schedule_interval=schedule,
        tags=['database'],
        catchup=False,
    )

    # Start task
    start = PythonOperator(
        task_id="start",
        python_callable=lambda: logging.info("Jobs started"),
        dag=dag
    )

    # Create a PythonOperator for purging old backups
    purge_old_backups_task = PythonOperator(
        task_id='purge_old_backups_task',
        python_callable=purge_old_backups,
        op_kwargs={
            'local_path': f'{backup_directory}',
            'repo_name': f'{backup_repository}',
            'conn_id': 'git_conn'
        },
        dag=dag,
    )

    # End task
    end = PythonOperator(
        task_id="end",
        python_callable=lambda: logging.info("Jobs completed successfully"),
        dag=dag
    )

    start >> purge_old_backups_task >> end
    
    return dag