# 📖 Liberty Airflow
### A Scalable and Extensible FastAPI and React Scheduler prebuilt with Airflow

# Airflow Setup Guide

## 📌 Prerequisites
Before installing Airflow, ensure you have the following installed on your system:
- **Python 3.12**
- **PostgreSQL** (for database storage)
- **Git** (if needed for repository usage)

## 🔧 Step 1: Create a `.env` File
Airflow requires environment variables to be set. Create a `.env` file in the project root and configure it as follows:

```ini
# Airflow and Python Version
AIRFLOW_VERSION=2.10.5
PYTHON_VERSION=3.12

# PostgreSQL Config
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_DB=test
POSTGRES_USER=test
POSTGRES_PASSWORD=your_password_here  # Replace with a secure password

# Admin PostgreSQL Config
POSTGRES_ADMIN_DB=liberty
POSTGRES_ADMIN_USER=liberty
POSTGRES_ADMIN_PASSWORD=your_secure_admin_password_here  # Replace with a secure password

# Airflow Config
AIRFLOW_HOME="./"
AIRFLOW__CORE__LOAD_EXAMPLES="False"
AIRFLOW__DATABASE__LOAD_DEFAULT_CONNECTIONS="False"
AIRFLOW__WEBSERVER__EXPOSE_CONFIG="True"
AIRFLOW__CORE__EXECUTOR="LocalExecutor"
AIRFLOW__WEBSERVER__WEB_SERVER_PORT=8081 # Replace with your port
AIRFLOW__WEBSERVER__BASE_URL="http://localhost:8081/airflow" # Replace with your URL
PYTHONWARNINGS="ignore::SyntaxWarning"
AIRFLOW__DATABASE__SQL_ALCHEMY_CONN=postgresql+psycopg2://${POSTGRES_USER}:${POSTGRES_PASSWORD}@${POSTGRES_HOST}:${POSTGRES_PORT}/${POSTGRES_DB}
AIRFLOW__WEBSERVER__SECRET_KEY=your_secret_key_here  # Replace with a secure secret key
# OSX issue only
# AIRFLOW__CORE__EXECUTOR=app.utils.local_executor.LocalExecutor 

# Git config
GIT_URL=http://your_git_token_here@localhost:3000/`repository`

# Default Airflow Admin User
AIRFLOW_ADMIN_USER=admin
AIRFLOW_ADMIN_EMAIL=admin@example.com
AIRFLOW_ADMIN_PASSWORD=your_admin_password_here  # Replace with a secure password
AIRFLOW_ADMIN_FIRSTNAME=Admin
AIRFLOW_ADMIN_LASTNAME=User
```

> ⚠ **IMPORTANT**: Do **not** commit the `.env` file to version control. Keep credentials secure.

---

## ▶ Step 2: Install Liberty Airflow

```sh
pip install liberty-airflow
```
This script will preconfigure the environment for Airflow installation

---

## ▶ Step 3: Install Airflow
To install Airflow and set up the database, run:

```sh
airflow-install
```
This script will:
- Install Airflow and required dependencies
- Create the PostgreSQL database and user (if not already created)
- Initialize the Airflow database
- Create a default Airflow admin user

---

## ▶ Step 4: Start Airflow
To start Airflow services, run:

```sh
airflow-start
```
This will:
- Start the Airflow Scheduler
- Start the Airflow Webserver

Once started, you can access Airflow at:
👉 **[http://localhost:8081/airflow](http://localhost:8081/airflow)**

---

## ⏹ Step 5: Stop Airflow
To stop all running Airflow processes, run:

```sh
airflow-stop
```
This will:
- Stop the Airflow Scheduler
- Stop the Airflow Webserver

---

## 🛠 Troubleshooting
- If Airflow does not start, check the logs in the `logs/` directory.
- Ensure PostgreSQL is running and accessible

---

## ✅ Next Steps
- Configure DAGs inside `$AIRFLOW_HOME/dags/`.
- Add Git integration using the configured `GIT_URL`.
- Secure your instance by updating passwords and secret keys.

---

## 💖 Sponsorship  
If you find **Liberty Ariflow** useful and would like to support its development, consider sponsoring us. Your contributions help maintain the project, add new features, and improve the documentation. Every contribution, big or small, is greatly appreciated!  

To sponsor, visit: **[GitHub Sponsors](https://github.com/sponsors/fblettner)** or reach out to us directly.  

---

## 📜 License  
Liberty Airflow is **open-source software** licensed under the **AGPL License**.  

---

## 📧 Contact & Support  
If you have questions or need support:  
- **Email**: [franck.blettner@nomana-it.fr](mailto:franck.blettner@nomana-it.fr)  
- **GitHub Issues**: [Report an issue](https://github.com/fblettner/liberty-airflow/issues)  
- **Discussions**: Join the conversation in the **GitHub Discussions** section.  

---

### ⭐ If you find Liberty Airflow useful, consider giving it a star on GitHub!  
```bash
git clone https://github.com/fblettner/liberty-airflow.git
cd liberty-framework
```

🚀 **Let's build the future of business applications together!** 🚀  
