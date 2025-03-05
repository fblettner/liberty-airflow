#
# Copyright (c) 2024 NOMANA-IT and/or its affiliates.
# All rights reserved. Use is subject to license terms.
#
from airflow import DAG
from airflow.models import Variable
from airflow.operators.python import PythonOperator, ShortCircuitOperator
from app.airflow.plugins.database.postgres.db_backup import pg_dump
from app.airflow.plugins.database.postgres.db_meta import pg_get_databases
from app.airflow.plugins.git.utils import push_backup
import logging

def backup_db_dag(dag_id, schedule, default_args):
    """
    Creates a DAG to Backup PostgreSQL database.
    
    :param dag_id: ID of the DAG
    :param schedule: Schedule interval of the DAG
    :param default_args: Default arguments for the DAG
    :return: DAG object
    """
    dag = DAG(
        dag_id=dag_id,
        default_args=default_args,
        description='Backup PostgreSQL databases for Liberty Framework',
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

    # Retrieve the list of databases by querying PostgreSQL
    databases = pg_get_databases(conn_id="liberty_conn")

    # Create individual backup tasks for each database
    backup_tasks = [pg_dump(dag, db, conn_id="liberty_conn") for db in databases]

    # Get backup directory from Airflow variable
    backup_directory = Variable.get("backup_directory", default_var=30)
    backup_repository = Variable.get("backup_repository", default_var=30)
    backup_to_git = Variable.get("backup_to_git", default_var="False").lower() in ("true", "1", "yes", "y")

    check_backup_to_git = ShortCircuitOperator(
        task_id='check_backup_to_git',
        python_callable=lambda: backup_to_git,  # Stops if False
        dag=dag,
    )

    # Step 2: Create the push task using PythonOperator
    push_all_backups_task = PythonOperator(
        task_id='push_all_backups_to_git',
        python_callable=push_backup,
        op_kwargs={
            'local_path': f'{backup_directory}',
            'repo_name': f'{backup_repository}',
            'databases': databases,
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

    # Set task dependencies: all backups must complete before pushing
    start >> backup_tasks >> check_backup_to_git >> push_all_backups_task >> end

    return dag