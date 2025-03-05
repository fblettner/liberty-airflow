# liberty_utils.py
from pyspark.sql import SparkSession
from airflow.providers.postgres.hooks.postgres import PostgresHook
import logging
from app.airflow.plugins.database.utils.db_meta import get_connection


# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def create_spark_session() -> SparkSession:
    spark_session = SparkSession\
        .builder\
        .appName("LIBERTY") \
        .config("spark.sql.debug.maxToStringFields", "-1") \
        .config("spark.jars", "/opt/spark/jars/ojdbc11.jar,/opt/spark/jars/postgresql-42.7.4.jar") \
        .getOrCreate()

    return spark_session


def get_all_tables(spark, conn):
    """Retrieve all tables (both with and without foreign keys)."""
    # Query to fetch tables without foreign keys
    query_no_fk = f"""
        SELECT
            table_name
        FROM
            information_schema.tables
        WHERE
            table_schema = '{conn['schema']}'
            AND table_type = 'BASE TABLE'
            AND table_name NOT IN (
                SELECT DISTINCT kcu.table_name
                FROM information_schema.table_constraints AS tc
                JOIN information_schema.key_column_usage AS kcu
                    ON tc.constraint_name = kcu.constraint_name
                    AND tc.table_schema = kcu.table_schema
                WHERE tc.constraint_type = 'FOREIGN KEY'
            )
    """

    # Fetch tables without foreign keys
    no_fk_df = spark.read \
        .format("jdbc") \
        .option("url", conn["url"]) \
        .option("driver", conn["driver"]) \
        .option("dbtable", f"({query_no_fk}) AS no_fk_tables") \
        .option("user", conn["user"]) \
        .option("password", conn["password"]) \
        .load()

    # Collect the list of tables without foreign keys
    no_fk_tables = [row['table_name'] for row in no_fk_df.collect()]

    # Fetch foreign key dependencies 
    fk_dependencies = get_foreign_key_dependencies(spark, conn)
    
    return no_fk_tables, fk_dependencies

def get_foreign_key_dependencies(spark, conn):
    """Retrieve the foreign key dependencies between tables."""
    query = f"""
        SELECT
            kcu.table_name AS source_table,
            rel_kcu.table_name AS target_table
        FROM
            information_schema.table_constraints tco
            JOIN information_schema.key_column_usage kcu
                ON tco.constraint_schema = kcu.constraint_schema
                AND tco.constraint_name = kcu.constraint_name
            JOIN information_schema.referential_constraints rco
                ON tco.constraint_schema = rco.constraint_schema
                AND tco.constraint_name = rco.constraint_name
            JOIN information_schema.key_column_usage rel_kcu
                ON rco.unique_constraint_schema = rel_kcu.constraint_schema
                AND rco.unique_constraint_name = rel_kcu.constraint_name
                AND kcu.ordinal_position = rel_kcu.ordinal_position
        WHERE
            tco.constraint_type = 'FOREIGN KEY'
            AND kcu.table_schema = '{conn['schema']}'
    """

    fk_df = spark.read \
        .format("jdbc") \
        .option("url", conn["url"]) \
        .option("driver", conn["driver"]) \
        .option("dbtable", f"({query}) AS foreign_keys") \
        .option("user", conn["user"]) \
        .option("password", conn["password"]) \
        .load()

    return fk_df.collect()

from collections import defaultdict, deque

def topological_sort(dependencies):
    """Perform topological sort on the dependency graph."""
    in_degree = defaultdict(int)
    graph = defaultdict(list)

    for source, target in dependencies:
        graph[target].append(source)
        in_degree[source] += 1
        if target not in in_degree:
            in_degree[target] = 0

    queue = deque([table for table in in_degree if in_degree[table] == 0])
    sorted_tables = []

    while queue:
        table = queue.popleft()
        sorted_tables.append(table)

        for dependent in graph[table]:
            in_degree[dependent] -= 1
            if in_degree[dependent] == 0:
                queue.append(dependent)

    return sorted_tables
    
def get_primary_key_for_table(spark, table_name, conn):
    """Retrieve the primary key for a given table."""
    query = f"""
        SELECT kcu.column_name
        FROM information_schema.table_constraints AS tc
        JOIN information_schema.key_column_usage AS kcu
        ON tc.constraint_name = kcu.constraint_name
        AND tc.table_schema = kcu.table_schema
        WHERE tc.constraint_type = 'PRIMARY KEY' 
        AND tc.table_name = '{table_name}'
        AND tc.table_schema = '{conn['schema']}'
    """
    
    # Execute the query to get the primary key
    pk_df = spark.read \
        .format("jdbc") \
        .option("url", conn["url"]) \
        .option("driver", conn["driver"]) \
        .option("dbtable", f"({query}) AS pk_query") \
        .option("user", conn["user"]) \
        .option("password", conn["password"]) \
        .load()
    
    # Collect primary key columns to a list
    pk_columns = [row['column_name'] for row in pk_df.collect()]
    
    return pk_columns

def delete_existing_rows(target_conn, primary_keys, table, rows_to_update):    
    # Initialize PostgresHook
    pg_hook = PostgresHook(postgres_conn_id=target_conn["id"])

    # Collect primary key values from rows_to_update using renamed columns
    primary_key_conditions = []
    for pk in primary_keys:
        pk_values = [row[f"source_{pk}"] for row in rows_to_update.select(f"source_{pk}").collect()]  # Collect values
        
        # Format the values correctly based on their type (e.g., quote strings and dates)
        formatted_values = []
        for value in pk_values:
            if isinstance(value, str):
                formatted_values.append(f"'{value}'") 
            elif value is None:
                formatted_values.append("NULL") 
            else:
                formatted_values.append(str(value))  
        
        if formatted_values:
            # Join the formatted values for the IN clause
            primary_key_conditions.append(f"{pk} IN ({', '.join(formatted_values)})")
    
    # Join the conditions with AND to form the WHERE clause
    condition = " AND ".join(primary_key_conditions)
    
    if not condition:
        return  # No rows to delete, so we skip the deletion

    # SQL DELETE query to remove existing rows
    delete_query = f"DELETE FROM {target_conn['schema']}.{table} WHERE {condition}"

    # Use PostgresHook to execute the DELETE query
    try:
        pg_hook.run(delete_query)
    except Exception as e:
        logging.error(f"Error during DELETE execution: {str(e)}")
        raise
    

def merge_all_tables(conn_source, conn_target, source_schema, target_schema):
    # Initialize Spark session
    spark = create_spark_session()

    # JDBC connection properties for source and target databases
    source_conn = get_connection(conn_source, source_schema)
    target_conn = get_connection(conn_target, target_schema)

    # Get tables without foreign keys and foreign key dependencies
    no_fk_tables, fk_dependencies = get_all_tables(spark, source_conn)

    # Process tables without foreign keys first
    for table in no_fk_tables:
        merge_single_table(spark, table, source_conn, target_conn)

    # Process tables with foreign key dependencies in order
    processed_tables = set(no_fk_tables)  # Keep track of processed tables

    # Sort and process tables with foreign key dependencies
    while fk_dependencies:
        for dependency in fk_dependencies:
            source_table = dependency['source_table']
            target_table = dependency['target_table']

            if target_table in processed_tables:
                merge_single_table(spark, source_table, source_conn, target_conn)
                processed_tables.add(source_table)
                fk_dependencies.remove(dependency)

    spark.stop()

def merge_single_table(spark, table, source_conn, target_conn):
    primary_keys = get_primary_key_for_table(spark, table, source_conn)

    # If no primary keys are found, log a message and skip this table
    if not primary_keys:
        logger.warning(f"No primary key found for table {table}. Skipping replication for this table.")
        return  # Skip this table
    
    # Load data from the current table in the source PostgreSQL
    source_data_df = spark.read \
        .format("jdbc") \
        .option("url", source_conn["url"]) \
        .option("driver", source_conn["driver"]) \
        .option("dbtable", f"{source_conn['schema']}.{table}") \
        .option("numPartitions", source_conn["numPartitions"]) \
        .option("fetchsize", source_conn["fetchsize"]) \
        .option("user", source_conn["user"]) \
        .option("password", source_conn["password"]) \
        .load()

    # Load existing data from the target table
    target_data_df = spark.read \
        .format("jdbc") \
        .option("url", target_conn["url"]) \
        .option("driver", target_conn["driver"]) \
        .option("dbtable", f"{target_conn['schema']}.{table}") \
        .option("numPartitions", target_conn["numPartitions"]) \
        .option("fetchsize", target_conn["fetchsize"]) \
        .option("user", target_conn["user"]) \
        .option("password", target_conn["password"]) \
        .load()

    joined_df = source_data_df.alias("source").join(
        target_data_df.alias("target"), 
        [source_data_df[pk] == target_data_df[pk] for pk in primary_keys]
    )

    # Select all source columns with explicit "source_" prefix and target columns
    joined_df = joined_df.select(
        *[joined_df[f"source.{col}"].alias(f"source_{col}") for col in source_data_df.columns],
        *[joined_df[f"target.{col}"].alias(f"target_{col}") for col in target_data_df.columns]
    )

    # Step 5: Identify rows to insert (rows in source that don't exist in target)
    rows_to_insert = source_data_df.join(target_data_df, primary_keys, how="left_anti")
    num_rows_inserted = rows_to_insert.count()

    # Step 6: Identify rows to update (where source and target columns differ)
    rows_to_update = joined_df.filter(
        " OR ".join([f"source_{col} != target_{col}" for col in source_data_df.columns])
    )
    num_rows_updated = rows_to_update.count()

    # Step 4: Insert new rows into the target table
    rows_to_insert.write \
        .format("jdbc") \
        .option("driver", target_conn["driver"]) \
        .option("url", target_conn["url"]) \
        .option("dbtable", f"{target_conn['schema']}.{table}") \
        .option("user", target_conn["user"]) \
        .option("password", target_conn["password"]) \
        .option("numPartitions", target_conn["numPartitions"]) \
        .option("batchsize", target_conn["batchsize"]) \
        .mode("append") \
        .save()

    # delete existing rows from the target table that need to be updated
    delete_existing_rows(target_conn, primary_keys, table, rows_to_update)

    # Step 7: Re-fetch the target data after the deletion to ensure consistency
    target_data_df_after_delete = spark.read \
        .format("jdbc") \
        .option("url", target_conn["url"]) \
        .option("driver", target_conn["driver"]) \
        .option("dbtable", f"{target_conn['schema']}.{table}") \
        .option("numPartitions", target_conn["numPartitions"]) \
        .option("fetchsize", target_conn["fetchsize"]) \
        .option("user", target_conn["user"]) \
        .option("password", target_conn["password"]) \
        .load()

    # Step 8: Re-identify rows to insert (those that don’t exist in the target after the delete)
    rows_to_insert = source_data_df.join(target_data_df_after_delete, primary_keys, how="left_anti")

    # Step 9: Insert new rows into the target table
    rows_to_insert.write \
        .format("jdbc") \
        .option("driver", target_conn["driver"]) \
        .option("url", target_conn["url"]) \
        .option("dbtable", f"{target_conn['schema']}.{table}") \
        .option("user", target_conn["user"]) \
        .option("password", target_conn["password"]) \
        .option("numPartitions", target_conn["numPartitions"]) \
        .option("batchsize", target_conn["batchsize"]) \
        .mode("append") \
        .save()

    # Log the number of rows inserted and updated
    logger.info(f"Table {table}: {num_rows_inserted} rows inserted, {num_rows_updated} rows updated.")
