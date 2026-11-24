import os
import mysql.connector
import streamlit as st
from dotenv import load_dotenv

load_dotenv()


def create_connection(database=None):
    try:
        connection = mysql.connector.connect(
            host=os.getenv("MYSQL_HOST", "localhost"),
            user=os.getenv("MYSQL_USER", "root"),
            password=os.getenv("MYSQL_PASSWORD", ""),
            database=database
        )
        return connection

    except mysql.connector.Error as error:
        st.error(f"Database Connection Error: {error}")
        return None


def get_databases():
    connection = create_connection()

    if connection is None:
        return []

    try:
        cursor = connection.cursor()
        cursor.execute("SHOW DATABASES")

        system_databases = {
            "information_schema",
            "mysql",
            "performance_schema",
            "sys"
        }

        databases = [
            row[0]
            for row in cursor.fetchall()
            if row[0] not in system_databases
        ]

        cursor.close()
        return databases

    except mysql.connector.Error as error:
        st.error(f"Database Discovery Error: {error}")
        return []

    finally:
        connection.close()


def get_tables(database):
    connection = create_connection(database)

    if connection is None:
        return []

    try:
        cursor = connection.cursor()
        cursor.execute("SHOW TABLES")

        tables = [row[0] for row in cursor.fetchall()]

        cursor.close()
        return tables

    except mysql.connector.Error as error:
        st.error(f"Table Discovery Error: {error}")
        return []

    finally:
        connection.close()


def get_table_schema(database, table):
    connection = create_connection(database)

    if connection is None:
        return []

    try:
        cursor = connection.cursor(dictionary=True)

        query = """
            SELECT
                COLUMN_NAME,
                DATA_TYPE,
                IS_NULLABLE,
                COLUMN_KEY
            FROM information_schema.COLUMNS
            WHERE TABLE_SCHEMA = %s
            AND TABLE_NAME = %s
            ORDER BY ORDINAL_POSITION
        """

        cursor.execute(query, (database, table))
        columns = cursor.fetchall()

        cursor.close()
        return columns

    except mysql.connector.Error as error:
        st.error(f"Schema Discovery Error: {error}")
        return []

    finally:
        connection.close()


def get_database_schema(database):
    schema = {}

    tables = get_tables(database)

    for table in tables:
        schema[table] = get_table_schema(database, table)

    return schema


def execute_query(query, database="company_db1"):
    connection = create_connection(database)

    if connection is None:
        return None

    cursor = None

    try:
        cursor = connection.cursor(dictionary=True)
        cursor.execute(query)

        if cursor.with_rows:
            results = cursor.fetchall()
        else:
            connection.commit()
            results = []

        return results

    except mysql.connector.Error as error:
        st.error(f"SQL Execution Error: {error}")
        return None

    finally:
        if cursor is not None:
            cursor.close()

        connection.close()