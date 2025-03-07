from airflow.providers.postgres.hooks.postgres import PostgresHook
from pyspark.sql import SparkSession, DataFrame
from pyspark.sql.types import IntegerType, StringType
import logging

# Function to retrieve the list of databases using a PostgreSQL query
def pg_get_databases(conn_id="postgres_conn"):
    # Use PostgresHook to connect to the database and execute the query
    pg_hook = PostgresHook(postgres_conn_id=conn_id)
    
    # Query to list databases (this can vary depending on PostgreSQL setup)
    sql = "SELECT datname FROM pg_database WHERE datistemplate = false;"
    
    # Execute the query and fetch the result
    connection = pg_hook.get_conn()
    cursor = connection.cursor()
    cursor.execute(sql)
    results = cursor.fetchall()
    
    # Return the list of database names
    return [row[0] for row in results]


def pg_get_connection(connection, schema=None):
    """Helper function to create a PostgreSQL JDBC connection dictionary."""
    schema = schema if schema else connection.login
    return {
        "id": connection.conn_id,
        "url": f"jdbc:postgresql://{connection.host}:{connection.port}/{connection.schema}",
        "driver": "org.postgresql.Driver",
        "host": connection.host,
        "port": connection.port,
        "database": connection.schema,
        "schema": schema,
        "user": connection.login,
        "password": connection.password,
        "numPartitions": 5,
        "fetchsize": 1000,
        "batchsize": 1000
    }


def pg_get_column_lengths(spark: SparkSession, table: str, schema: str, conn_source: dict) -> dict:
    query = f"""
    SELECT column_name, character_maximum_length
    FROM information_schema.columns
    WHERE table_schema = '{schema}' AND table_name = '{table}'
    """

    column_metadata_df = spark.read \
        .format("jdbc") \
        .option("url", conn_source["url"]) \
        .option("driver", conn_source["driver"]) \
        .option("query", query) \
        .option("numPartitions", conn_source["numPartitions"]) \
        .option("fetchsize", conn_source["fetchsize"]) \
        .option("user", conn_source["user"]) \
        .option("password", conn_source["password"]) \
        .load()

    column_lengths = {row["column_name"]: row["character_maximum_length"] for row in column_metadata_df.collect()}
    
    return column_lengths

def pg_get_column_types(data_df: DataFrame, column_lengths: dict) -> str:
    column_types = []
    for field in data_df.schema.fields:
        if isinstance(field.dataType, StringType):
            column_length = column_lengths.get(field.name.lower(), 255)
            column_types.append(f"{field.name} VARCHAR({column_length})")
        elif isinstance(field.dataType, IntegerType):
            column_types.append(f"{field.name} INTEGER")
        else:
            pass
    return ", ".join(column_types)


