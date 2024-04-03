#!/usr/bin/env python3

import psycopg2

# Database connection details
DB1_NAME = "mercadona-v16.0"
DB1_USER = "didac"
DB1_PASSWORD = False  # Leave empty for password-less authentication
DB1_HOST = "localhost"

DB2_NAME = "steam-franchise-v16.0-dev"
DB2_USER = "didac"
DB2_PASSWORD = False  # Leave empty for password-less authentication
DB2_HOST = "localhost"

def compare_tables(db1_conn, db2_conn, table_name):
    # Query to select data from table
    query = f"SELECT * FROM {table_name}"

    # Execute query on database 1
    db1_cursor = db1_conn.cursor()
    db1_cursor.execute(query)
    db1_data = db1_cursor.fetchall()

    # Execute query on database 2
    db2_cursor = db2_conn.cursor()
    db2_cursor.execute(query)
    db2_data = db2_cursor.fetchall()

    # Compare data row by row
    differences_found = False
    for row1, row2 in zip(db1_data, db2_data):
        if row1 != row2:
            differences_found = True
            print(f"Difference found in table '{table_name}':")
            print(f"Database 1 row: {row1}")
            print(f"Database 2 row: {row2}")

    if not differences_found:
        print(f"Data in table '{table_name}' is identical in both databases.")

if __name__ == "__main__":
    # Connect to the databases
    db1_conn = psycopg2.connect(
        dbname=DB1_NAME, user=DB1_USER, password=DB1_PASSWORD, host=DB1_HOST)
    db2_conn = psycopg2.connect(
        dbname=DB2_NAME, user=DB2_USER, password=DB2_PASSWORD, host=DB2_HOST)

    # Specify the table to compare
    table_name = "product_product"

    # Compare tables
    compare_tables(db1_conn, db2_conn, table_name)

    # Close connections
    db1_conn.close()
    db2_conn.close()
