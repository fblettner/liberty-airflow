import os
import subprocess
import psycopg2
from app.utils.utils import load_env

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

if __name__ == "__main__":
    install_airflow()