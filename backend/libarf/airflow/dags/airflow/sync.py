from airflow import DAG
from airflow.operators.python import PythonOperator
from libarf.airflow.plugins.git.utils import pull_repository
import logging

def sync_repo_dag(dag_id, schedule, default_args):
    """
    Creates a DAG to sync git repository in airflow
    
    :param dag_id: ID of the DAG
    :param schedule: Schedule interval of the DAG
    :param default_args: Default arguments for the DAG
    :return: DAG object
    """
    dag = DAG(
        dag_id=dag_id,
        default_args=default_args,
        description='Synchronize dags and plugins from Git',
        schedule_interval=schedule,
        tags=['airflow'],
        catchup=False,
    )

    # List of repositories and their corresponding paths
    repos = [
        {'local_path': '/opt/airflow/dags/custom', 'repo_name': 'airflow-custom-dags'},
        {'local_path': '/opt/airflow/plugins/custom', 'repo_name': 'airflow-custom-plugins'}
    ]

    # Start task
    start = PythonOperator(
        task_id="start",
        python_callable=lambda: logging.info("Jobs started"),
        dag=dag
    )

    # Create tasks dynamically for each repository
    sync_tasks = []
    for repo in repos:
        task = PythonOperator(
            task_id=f'pull_{repo["repo_name"]}',
            python_callable=pull_repository,
            op_kwargs=repo,
            dag=dag,
        )
        sync_tasks.append(task)


    # End task
    end = PythonOperator(
        task_id="end",
        python_callable=lambda: logging.info("Jobs completed successfully"),
        dag=dag
    )

    # Set dependencies: Start -> Sync tasks -> End
    start >> sync_tasks >> end

    return dag