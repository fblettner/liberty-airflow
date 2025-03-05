#
# Copyright (c) 2024 NOMANA-IT and/or its affiliates.
# All rights reserved. Use is subject to license terms.
#
from airflow import DAG
from airflow.operators.python import PythonOperator
from app.airflow.plugins.airflow.purge import (
    dag_runs,
    task_instances,
    jobs,
    logs_on_disk,
    logs_in_db
)

def purge_airflow_dag(dag_id, schedule, default_args):
    """
    Creates a DAG to purge old DAG runs, task instances, jobs, and logs.
    
    :param dag_id: ID of the DAG
    :param schedule: Schedule interval of the DAG
    :param default_args: Default arguments for the DAG
    :return: DAG object
    """
    dag = DAG(
        dag_id=dag_id,
        default_args=default_args,
        description='Purge old DAG runs, task instances, jobs, and logs',
        schedule_interval=schedule,
        tags=['airflow'],
        catchup=False,
    )

    # List of purge tasks
    purge_tasks = [
        {'task_id': 'purge_old_dag_runs', 'python_callable': dag_runs},
        {'task_id': 'purge_old_task_instances', 'python_callable': task_instances},
        {'task_id': 'purge_old_jobs', 'python_callable': jobs},
        {'task_id': 'purge_old_logs_on_disk', 'python_callable': logs_on_disk},
        {'task_id': 'purge_old_logs_in_db', 'python_callable': logs_in_db},
    ]

    # Dynamically create tasks
    previous_task = None
    for task_info in purge_tasks:
        task = PythonOperator(
            task_id=task_info['task_id'],
            python_callable=task_info['python_callable'],
            dag=dag,
        )
        
        # Set task dependencies (chain the tasks)
        if previous_task:
            previous_task >> task
        previous_task = task
    
    return dag