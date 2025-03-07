from airflow.hooks.base import BaseHook
from pyspark.sql import SparkSession, DataFrame
from pyspark.sql.types import IntegerType, StringType

def ora_get_connection(connection, schema=None):
    """Helper function to create an Oracle JDBC connection dictionary."""
    schema = schema if schema else connection.login
    return {
        "id": connection.conn_id,
        "url": f"jdbc:oracle:thin:@//{connection.host}:{connection.port}/{connection.schema}",
        "driver": "oracle.jdbc.driver.OracleDriver",
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

def ora_get_column_lengths(spark: SparkSession, table: str, schema: str, conn_source: dict) -> dict:
    query = f"""
    SELECT COLUMN_NAME, CAST(DATA_LENGTH AS INTEGER) AS DATA_LENGTH
    FROM ALL_TAB_COLUMNS 
    WHERE TABLE_NAME = '{table}' AND OWNER = '{schema}'
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

    column_lengths = {row["COLUMN_NAME"]: row["DATA_LENGTH"] for row in column_metadata_df.collect()}
    
    return column_lengths

def ora_get_column_types(data_df: DataFrame, column_lengths: dict) -> str:
    column_types = []
    for field in data_df.schema.fields:
        if isinstance(field.dataType, StringType):
            column_length = column_lengths.get(field.name.upper(), 255)
            column_types.append(f"{field.name} VARCHAR({column_length})")
        elif isinstance(field.dataType, IntegerType):
            column_types.append(f"{field.name} INTEGER")
        else:
            # Handle other types as needed
            pass
    return ", ".join(column_types)
