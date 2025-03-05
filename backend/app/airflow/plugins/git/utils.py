#
# Copyright (c) 2024 NOMANA-IT and/or its affiliates.
# All rights reserved. Use is subject to license terms.
#
from airflow.hooks.base import BaseHook
from airflow.models import Variable
import subprocess
import logging
import os
from datetime import datetime, timedelta

def pull_repository(local_path, repo_name, conn_id="git_conn"):
    """Pull the latest changes from the repository using the repo name and base URL from Airflow connection."""
    
    # Retrieve the connection
    connection = BaseHook.get_connection(conn_id)
    
    # If login is empty, construct URL with only the token
    if connection.login:
        base_url = f"http://{connection.login}:{connection.password}@{connection.host}/{connection.schema}/"
    else:
        base_url = f"http://{connection.password}@{connection.host}/{connection.schema}/"  # Only use the token
    
    # Construct the full repository URL
    repo_url = f"{base_url}{repo_name}.git"
    
    try:
        # Pull the latest changes
        logging.info(f"Pulling the latest changes for repository: {repo_url}")
        subprocess.run(f"cd {local_path} && git pull", shell=True, check=True)
        logging.info(f"Successfully pulled repository: {repo_url}")
    
    except subprocess.CalledProcessError as e:
        logging.error(f"Failed to pull repository: {repo_url} - {e}")
        raise


def push_backup(local_path, repo_name, databases, conn_id="git_conn"):
    """Push backups for all databases to Git using the base URL from Airflow connection."""
    
    # Retrieve the connection
    connection = BaseHook.get_connection(conn_id)
    
    # If login is empty, construct URL with only the token
    if connection.login:
        base_url = f"http://{connection.login}:{connection.password}@{connection.host}/{connection.schema}/"
    else:
        base_url = f"http://{connection.password}@{connection.host}/{connection.schema}/"  # Only use the token
    
    # Construct the full repository URL
    repo_url = f"{base_url}{repo_name}.git"
    
    try:
        today_date = datetime.now().strftime('%Y-%m-%d')

        if os.path.exists(os.path.join(local_path, ".git")):
            print("Git repository found, pulling latest changes...")
            os.chdir(local_path)
            subprocess.run("git pull", shell=True, check=True)
        else:
            print("No git repository found, cloning repository...")
            subprocess.run(f"git clone {repo_url} {local_path}", shell=True, check=True)

        # Configure Git user details
        subprocess.run('git config user.email "liberty@nomana-it.fr"', shell=True, check=True)
        subprocess.run('git config user.name "Liberty Backup Bot"', shell=True, check=True)

        # Create a folder for today's backups
        os.makedirs(today_date, exist_ok=True)
        airflow_home = os.getenv("AIRFLOW_HOME", os.getcwd())

        # Move all backup files into the dated folder and compress them
        for db in databases:
            backup_file = f"{airflow_home}/tmp/{db}_dump.sql"
            if os.path.exists(backup_file):
                # Compress the backup file
                subprocess.run(f"gzip {backup_file}", shell=True, check=True)
                
                # Move the compressed file to the folder
                compressed_file = f"{airflow_home}/tmp/{db}_dump.sql.gz"
                subprocess.run(f"mv {compressed_file} {today_date}/{db}_dump.sql.gz", shell=True, check=True)

        # Check if there are any changes to commit
        git_status = subprocess.run("git status --porcelain", shell=True, capture_output=True, text=True)

        if git_status.stdout.strip():  # If there are changes (non-empty output)
            logging.info("Changes detected. Committing and pushing backups.")

            # Stage the changes
            subprocess.run(f"git add {today_date}/*.gz", shell=True, check=True)

            # Commit and push the changes
            subprocess.run(f'git commit -m "Backups for all Liberty databases on {today_date}"', shell=True, check=True)
            subprocess.run("git push", shell=True, check=True)

            logging.info(f"Successfully pushed all backups to {repo_url}.")
        else:
            logging.info("No changes detected. Skipping commit and push.")
    
    except subprocess.CalledProcessError as e:
        logging.error(f"Failed to push backups to {repo_url}: {e}")
        raise    

def purge_old_backups(local_path, repo_name, conn_id="git_conn"):
    """Purge backup files older than 30 days from Git"""
    try:
        # Pull the latest changes first using pull_repository function
        pull_repository(local_path, repo_name, conn_id)

        # Navigate to the local backup directory
        os.chdir(f"{local_path}")

        # Get retention period from Airflow variable and log it
        backup_retention_days = int(Variable.get("backup_retention_days", default_var=30))
        logging.info(f"Backup retention days set to: {backup_retention_days}")

        # Calculate the cutoff date (set time to midnight) and log it
        cutoff_date = (datetime.now() - timedelta(days=backup_retention_days)).replace(hour=0, minute=0, second=0, microsecond=0)

        # Track if any directories were deleted
        deleted_any = False

        # Loop through directories with the format 'YYYY-MM-DD'
        for dir_name in os.listdir('.'):
            if os.path.isdir(dir_name) and len(dir_name) == 10:  # Check for date-like directories
                try:
                    # Parse the directory name as a date and log it
                    dir_date = datetime.strptime(dir_name, '%Y-%m-%d')

                    # Check if the directory is older than or equal to the cutoff date and log the comparison
                    if dir_date <= cutoff_date:
                        logging.info(f"Deleting old backup directory: {dir_name}")
                        subprocess.run(f"rm -rf {dir_name}", shell=True, check=True)
                        deleted_any = True  # Mark that we deleted something


                except ValueError:
                    # Skip directories that don't match the date format
                    logging.info(f"Skipping non-date directory: {dir_name}")
                    continue

        # Check if there are any changes in the working directory
        if deleted_any:
            git_status = subprocess.run("git status --porcelain", shell=True, capture_output=True, text=True)

            if git_status.stdout.strip():  # If there are changes (non-empty output)
                logging.info("Changes detected. Committing and pushing deletions.")

                # Stage the deletions
                subprocess.run('git config user.email "liberty@nomana-it.fr"', shell=True, check=True)
                subprocess.run('git config user.name "Liberty Backup Bot"', shell=True, check=True)
                subprocess.run("git add -A", shell=True, check=True)

                # Commit and push the changes
                subprocess.run("git commit -m 'Purge backups older than 30 days'", shell=True, check=True)
                subprocess.run("git push", shell=True, check=True)

                logging.info("Successfully purged old backups and pushed changes to Git.")
        else:
            logging.info("No changes detected. Skipping commit and push.")

    except subprocess.CalledProcessError as e:
        logging.error(f"Failed to purge old backups: {e}")
        raise