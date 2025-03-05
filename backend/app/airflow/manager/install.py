#
# Copyright (c) 2025 NOMANA-IT and/or its affiliates.
# All rights reserved. Use is subject to license terms.
#
import os
import shutil
import subprocess
import psycopg2
from app.utils.utils import load_env
from app.airflow.drivers import get_drivers_path
from app.airflow.config import get_config_path
from app.dags import get_dags_path

def create_postgres_db():
    """Creates the PostgreSQL database and role for Airflow."""
    try:
        # Load environment variables
        load_env()
        
        # Get PostgreSQL connection details from env variables
        postgres_host = os.getenv("POSTGRES_HOST", "localhost")
        postgres_port = os.getenv("POSTGRES_PORT", "5432")
        postgres_db = os.getenv("POSTGRES_DB", "airflow")
        postgres_user = os.getenv("POSTGRES_USER", "airflow")
        postgres_password = os.getenv("POSTGRES_PASSWORD", "airflow")

        postgres_admin_db = os.getenv("POSTGRES_ADMIN_DB", "postgres")
        postgres_admin_user = os.getenv("POSTGRES_ADMIN_USER", "postgres")
        postgres_admin_password = os.getenv("POSTGRES_ADMIN_PASSWORD", "securepassword")

        # Connect to PostgreSQL (default 'postgres' database)
        conn = psycopg2.connect(
            dbname=postgres_admin_db,
            user=postgres_admin_user,
            password=postgres_admin_password,
            host=postgres_host,
            port=postgres_port
        )
        conn.autocommit = True
        cur = conn.cursor()

        # Create the Airflow role (if not exists)
        cur.execute(f"SELECT 1 FROM pg_roles WHERE rolname='{postgres_user}';")
        if not cur.fetchone():
            cur.execute(f"CREATE ROLE {postgres_user} WITH LOGIN PASSWORD '{postgres_password}';")
            print(f"Created PostgreSQL role: {postgres_user}")

        # Create the Airflow database (if not exists)
        cur.execute(f"SELECT 1 FROM pg_database WHERE datname='{postgres_db}';")
        if not cur.fetchone():
            cur.execute(f"CREATE DATABASE {postgres_db} OWNER {postgres_user};")
            print(f"Created PostgreSQL database: {postgres_db}")

        cur.close()
        conn.close()

    except Exception as e:
        print(f"Error setting up PostgreSQL: {e}")
        exit(1)


def create_airflow_admin():
    """Creates the default admin user for Airflow."""
    admin_user = os.getenv("AIRFLOW_ADMIN_USER", "admin")
    admin_email = os.getenv("AIRFLOW_ADMIN_EMAIL", "admin@example.com")
    admin_password = os.getenv("AIRFLOW_ADMIN_PASSWORD", "admin")
    admin_firstname = os.getenv("AIRFLOW_ADMIN_FIRSTNAME", "Admin")
    admin_lastname = os.getenv("AIRFLOW_ADMIN_LASTNAME", "User")

    print("Creating default Airflow admin user...")

    create_user_cmd = f"""
    airflow users create \
        --username {admin_user} \
        --firstname {admin_firstname} \
        --lastname {admin_lastname} \
        --role Admin \
        --email {admin_email} \
        --password {admin_password}
    """
    subprocess.run(create_user_cmd, shell=True, check=True)

    print("Airflow admin user created successfully.")

def copy_drivers():
    """Copies only .jar JDBC drivers to the Airflow drivers directory."""
    airflow_home = os.getenv("AIRFLOW_HOME", os.getcwd())
    drivers_dir = os.path.join(airflow_home, "drivers")
    os.makedirs(drivers_dir, exist_ok=True)
    
    package_drivers_dir = get_drivers_path()
    print(package_drivers_dir)
    if os.path.exists(package_drivers_dir):
        for driver_file in os.listdir(package_drivers_dir):
            if driver_file.endswith(".jar"):  # Only copy .jar files
                src_path = os.path.join(package_drivers_dir, driver_file)
                dest_path = os.path.join(drivers_dir, driver_file)
                if os.path.isfile(src_path):
                    shutil.copy2(src_path, dest_path)
                    print(f"Copied {driver_file} to {drivers_dir}")
    else:
        print("No drivers directory found in package.")

def upload_config():
    """Uploads Airflow variables and connections from config directory to the database."""
    config_dir = get_config_path()
    
    if os.path.exists(os.path.join(config_dir, "variables.json")):
        subprocess.run(f"airflow variables import {os.path.join(config_dir, 'variables.json')}", shell=True, check=True)
        print("Imported Airflow variables.")
    
    if os.path.exists(os.path.join(config_dir, "connections.json")):
        subprocess.run(f"airflow connections import {os.path.join(config_dir, 'connections.json')}", shell=True, check=True)
        print("Imported Airflow connections.")

def copy_dags():
    """Copies only .py to the Airflow Dags Direcotry."""
    airflow_home = os.getenv("AIRFLOW_HOME", os.getcwd())
    drivers_dir = os.path.join(airflow_home, "dags")
    os.makedirs(drivers_dir, exist_ok=True)
    
    package_drivers_dir = get_dags_path()
    print(package_drivers_dir)
    if os.path.exists(package_drivers_dir):
        for driver_file in os.listdir(package_drivers_dir):
            src_path = os.path.join(package_drivers_dir, driver_file)
            dest_path = os.path.join(drivers_dir, driver_file)
            if os.path.isfile(src_path):
                shutil.copy2(src_path, dest_path)
                print(f"Copied {driver_file} to {drivers_dir}")
    else:
        print("No drivers directory found in package.")

def install_airflow():
    load_env()
    airflow_version = os.getenv("AIRFLOW_VERSION", "2.10.2")  
    python_version = os.getenv("PYTHON_VERSION", "3.12")  

    constraint_url = f"https://raw.githubusercontent.com/apache/airflow/constraints-{airflow_version}/constraints-{python_version}.txt"

    commands = [
        f'pip install "apache-airflow[celery,postgres]=={airflow_version}" --constraint "{constraint_url}"',
        "pip install apache-airflow-providers-apache-spark pyspark apache-airflow-providers-oracle apache-airflow-providers-postgres"
    ]

    for cmd in commands:
        subprocess.run(cmd, shell=True, check=True)

    print("Airflow installed successfully.")

    # Create PostgreSQL DB and Role
    create_postgres_db()

    # Initialize Airflow DB
    print("Initializing Airflow database...")
    subprocess.run("airflow db init", shell=True, check=True)
    print("Airflow database initialized.")    

    # Create the admin user after db init
    create_airflow_admin() 

    # Create Directories
    airflow_home = os.getenv("AIRFLOW_HOME", os.getcwd())
    os.makedirs(os.path.join(airflow_home, "tmp"), exist_ok=True)
    os.makedirs(os.path.join(airflow_home, "dags"), exist_ok=True)
    os.makedirs(os.path.join(airflow_home, "backup"), exist_ok=True)
    os.makedirs(os.path.join(airflow_home, "plugins"), exist_ok=True)
    os.makedirs(os.path.join(airflow_home, "drivers"), exist_ok=True)
    
    copy_drivers()
    upload_config()
    copy_dags()

if __name__ == "__main__":
    install_airflow()