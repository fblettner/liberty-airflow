from pyspark.sql import SparkSession, DataFrame
from airflow.hooks.base import BaseHook
from libarf.airflow.plugins.database.oracle.db_meta import ora_get_connection, ora_get_column_lengths, ora_get_column_types
from libarf.airflow.plugins.database.postgres.db_meta import pg_get_column_lengths, pg_get_column_types, pg_get_connection
import logging

def get_column_lengths(spark: SparkSession, table: str, schema: str, conn_source: dict) -> dict:
    if conn_source["driver"] == "oracle.jdbc.driver.OracleDriver":
        return ora_get_column_lengths(spark, table, schema, conn_source)
    elif conn_source["driver"] == "org.postgresql.Driver":
        return pg_get_column_lengths(spark, table, schema, conn_source)
    else:
        raise ValueError(f"Unsupported database driver: {conn_source['driver']}")

def get_column_types(data_df: DataFrame, column_lengths: dict, conn_source: dict) -> str:
    if conn_source["driver"] == "oracle.jdbc.driver.OracleDriver":
        return ora_get_column_types(data_df, column_lengths)
    elif conn_source["driver"] == "org.postgresql.Driver":
        return pg_get_column_types(data_df, column_lengths)
    else:
        raise ValueError(f"Unsupported database driver: {conn_source['driver']}")

def get_connection(conn_id, schema=None):
    """Retrieve the Airflow connection details dynamically based on the database type."""
    connection = BaseHook.get_connection(conn_id)
    
    conn_type = connection.conn_type.lower()

    if conn_type == "oracle":
        return ora_get_connection(connection, schema)
    elif conn_type == "postgres":
        return pg_get_connection(connection, schema)
    else:
        raise ValueError(f"Unsupported database type: {conn_type}")