import os
from airflow.operators.bash import BashOperator
from libarf.airflow.plugins.database.utils.db_meta import get_connection


# Updated function to create the backup tasks for each database using connection service
def pg_dump(dag, database_name, conn_id="postgres_conn"):
    # Retrieve the PostgreSQL connection details
    conn = get_connection(conn_id)
    airflow_home = os.getenv("AIRFLOW_HOME", os.getcwd())
    
    # Step 1: Perform PostgreSQL Backup using pg_dump
    backup_command = f"""
        set -x  # Log each command as it is executed
        PGPASSWORD={conn['password']} pg_dump -U {conn['user']} -h {conn['host']} -p {conn['port']} {database_name} > {airflow_home}/tmp/{database_name}_dump.sql
        echo "Backup completed for {database_name}"
    """

    backup_task = BashOperator(
        task_id=f'backup_postgres_{database_name}',
        bash_command=backup_command,
        dag=dag,
    )
    return backup_task