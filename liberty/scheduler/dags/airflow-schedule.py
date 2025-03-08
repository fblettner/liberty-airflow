#
# Copyright (c) 2025 NOMANA-IT and/or its affiliates.
# All rights reserved. Use is subject to license terms.
#
import pendulum

from liberty.airflow.dags.airflow.purge import purge_airflow_dag
from liberty.airflow.dags.airflow.sync import sync_repo_dag
from liberty.airflow.dags.database.backup import backup_db_dag
from liberty.airflow.dags.database.purge import purge_db_dag

# Default arguments for all DAGs
default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'start_date': pendulum.today("UTC").subtract(days=1),
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
}

# Daily DAGS
daily_dags_1 = purge_airflow_dag('airflow-purge-daily-1', '@daily', default_args)
daily_dags_2 = backup_db_dag('database-backup-daily-1', '00 1 * * *', default_args)

# Weekly DAGS
weekly_dags_1 = purge_db_dag('database-purge-weekly-1', '@weekly', default_args)

# Unscheduled DAGS
others_dags_2 = sync_repo_dag('airflow-sync-1', None, default_args)