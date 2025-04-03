import sqlite3
import os
import json
from login import *
import pytz
import datetime

db_name = "database.db"

def create_db(table='users', db_name="database.db", **columns):
    if not columns:
        columns = {
            "email": "TEXT UNIQUE NOT NULL",
            "password": "TEXT NOT NULL",
            "name": "TEXT",
            "reg_no": "TEXT",
            "session_id": "TEXT",
            "last_updated": "TEXT"
        }
    columns_str = ", ".join([f"{col_name} {col_type}" for col_name, col_type in columns.items()])
    with sqlite3.connect(db_name) as conn:
        c = conn.cursor()
        # Create table if it doesn’t exist
        c.execute(f"CREATE TABLE IF NOT EXISTS {table} (id INTEGER PRIMARY KEY, {columns_str})")
        print(f"Database and table '{table}' created or verified in '{db_name}'!")
        # Check and add missing columns
        existing_columns = {col[1] for col in c.execute(f"PRAGMA table_info({table})").fetchall()}
        for col_name, col_type in columns.items():
            if col_name not in existing_columns:
                try:
                    c.execute(f"ALTER TABLE {table} ADD COLUMN {col_name} {col_type}")
                    print(f"Added missing column '{col_name}' to '{table}'.")
                except sqlite3.OperationalError as e:
                    print(f"Error adding column '{col_name}': {e}")
        conn.commit()

def update_session_id(email, session_id):
    ist = pytz.timezone('Asia/Kolkata')
    timestamp = datetime.datetime.now(ist).strftime("%Y-%m-%d %H:%M:%S")
    modify_user(table="users", conditions={"email": email}, session_id=session_id, last_updated=timestamp)

def get_session_id(email):
    with sqlite3.connect("database.db") as conn:
        c = conn.cursor()
        c.execute("SELECT session_id, last_updated FROM users WHERE email = ?", (email,))
        result = c.fetchone()
        if result:
            session_id, last_updated = result
            ist = pytz.timezone('Asia/Kolkata')
            last_time = datetime.datetime.strptime(last_updated, "%Y-%m-%d %H:%M:%S")
            now = datetime.datetime.now(ist)
            if (now - last_time).total_seconds() < 3600:  # Refresh if older than 1 hour
                return session_id
            return None
        return None

def new_user(db_name="database.db", table="users", **user_data):
    columns = ", ".join(user_data.keys())
    placeholders = ", ".join("?" for _ in user_data)
    values = tuple(user_data.values())
    try:
        with sqlite3.connect(db_name) as conn:
            c = conn.cursor()
            c.execute(f"INSERT INTO {table} ({columns}) VALUES ({placeholders})", values)
            conn.commit()
            print("New user added successfully.", values)
            return True
    except sqlite3.IntegrityError:
        print("Error: Duplicate entry or constraint violation.")
        return False

def clear_db(table="users", db_name="database.db"):
    with sqlite3.connect(db_name) as conn:
        c = conn.cursor()
        c.execute(f"DELETE FROM {table}")
        conn.commit()
        print(f"All entries in '{table}' table cleared.")

def del_db(db_name="database.db"):
    try:
        os.remove(db_name)
        print(f"Database '{db_name}' deleted successfully.")
    except FileNotFoundError:
        print("No database found to delete.")

def del_user(table="users", db_name="database.db", **conditions):
    condition_str = " AND ".join([f"{col} = ?" for col in conditions])
    values = tuple(conditions.values())
    with sqlite3.connect(db_name) as conn:
        c = conn.cursor()
        c.execute(f"DELETE FROM {table} WHERE {condition_str}", values)
        conn.commit()
        print("User(s) deleted successfully.")

def read_user(table="users", db_name="database.db", **conditions):
    condition_str = " AND ".join([f"{col} = ?" for col in conditions])
    values = tuple(conditions.values())
    with sqlite3.connect(db_name) as conn:
        c = conn.cursor()
        query = f"SELECT * FROM {table} WHERE {condition_str}"
        c.execute(query, values)
        results = c.fetchall()
        for result in results:
            print(result)
        return results

def modify_user(table="users", db_name="database.db", conditions=None, **updates):
    if not conditions:
        print("No conditions provided for update.")
        return
    update_str = ", ".join([f"{col} = ?" for col in updates])
    condition_str = " AND ".join([f"{col} = ?" for col in conditions])
    values = tuple(updates.values()) + tuple(conditions.values())
    with sqlite3.connect(db_name) as conn:
        c = conn.cursor()
        c.execute(f"UPDATE {table} SET {update_str} WHERE {condition_str}", values)
        conn.commit()
        print("User modified successfully.")

def read_all(table="users", db_name="database.db"):
    with sqlite3.connect(db_name) as conn:
        c = conn.cursor()
        c.execute(f"SELECT * FROM {table}")
        results = c.fetchall()
        for row in results:
            print(row)
        return results

def read_table(table, db_name="database.db"):
    try:
        with sqlite3.connect(db_name) as conn:
            c = conn.cursor()
            c.execute(f"SELECT * FROM {table}")
            return c.fetchall()
    except sqlite3.OperationalError:
        print(f"Table '{table}' not found.")
        return None

def add_column(table="users", db_name="database.db", **columns):
    with sqlite3.connect(db_name) as conn:
        c = conn.cursor()
        try:
            for column_name, column_type in columns.items():
                c.execute(f"ALTER TABLE {table} ADD COLUMN {column_name} {column_type}")
                print(f"Column '{column_name}' added to table '{table}'.")
        except sqlite3.OperationalError as e:
            print(f"Error: {e}")

def del_column(column, table="users", db_name="database.db"):
    with sqlite3.connect(db_name) as conn:
        c = conn.cursor()
        try:
            c.execute(f"ALTER TABLE {table} DROP COLUMN {column}")
            print(f"Column '{column}' deleted from table '{table}'.")
        except sqlite3.OperationalError as e:
            print(f"Error: {e}")

def add_table(table="users", db_name="database.db", **columns):
    columns_str = ", ".join([f"{col_name} {col_type}" for col_name, col_type in columns.items()])
    with sqlite3.connect(db_name) as conn:
        c = conn.cursor()
        c.execute(f"CREATE TABLE IF NOT EXISTS {table} ({columns_str})")
        print(f"Table '{table}' created successfully.")

def del_table(table="users", db_name="database.db"):
    with sqlite3.connect(db_name) as conn:
        c = conn.cursor()
        try:
            c.execute(f"DROP TABLE IF EXISTS {table}")
            print(f"Table '{table}' deleted successfully.")
        except sqlite3.OperationalError:
            print(f"Table '{table}' not found.")

def store_js(file_data, email, column="bahikhata", table="users", db_name="database.db"):
    json_data = json.dumps(file_data)
    binary_data = json_data.encode('utf-8')
    with sqlite3.connect(db_name) as conn:
        c = conn.cursor()
        c.execute(f"SELECT 1 FROM {table} WHERE email = ?", (email,))
        exists = c.fetchone()
        if exists:
            c.execute(f"UPDATE {table} SET {column} = ? WHERE email = ?", (binary_data, email))
            print(f"Updated data for email '{email}' in the database.")
        else:
            c.execute(f"INSERT INTO {table} (email, {column}) VALUES (?, ?)", (email, binary_data))
            print(f"File stored successfully as a new entry linked to email '{email}'.")
        conn.commit()

def retrieve_js(email, column="bahikhata", table="users", db_name="database.db"):
    with sqlite3.connect(db_name) as conn:
        c = conn.cursor()
        c.execute(f"SELECT {column} FROM {table} WHERE email = ?", (email,))
        result = c.fetchone()
        if result:
            binary_data = result[0]
            try:
                json_data = json.loads(binary_data.decode('utf-8'))
                indented_json = json.dumps(json_data, indent=None)
                return indented_json
            except (UnicodeDecodeError, json.JSONDecodeError):
                print("Error: Failed to decode or parse JSON data.")
                return None
        else:
            print(f"No data found for email '{email}'.")
            return None

def get_pass(email, column="password", table="users", db_name="database.db"):
    with sqlite3.connect(db_name) as conn:
        c = conn.cursor()
        c.execute(f"SELECT {column} FROM {table} WHERE email = ?", (email,))
        result = c.fetchone()
        if result:
            return result[0]
        print("No password found for", email)
        return None

def get_stu(email, column="password", table="users", db_name="database.db"):
    with sqlite3.connect(db_name) as conn:
        c = conn.cursor()
        json_data = retrieve_js(email)
        try:
            indented_json = json.loads(json_data)
            StuID = indented_json["output"]["data"]["logindetails"]["Student"][0]["StuID"]
            if StuID:
                return StuID
            return None
        except Exception as e:
            print("Failed to fetch JSON file")
            return None

def db_login(email: str, password: str, table="users", db_name="database.db"):
    from login import login_check
    if login_check(email, password):
        with sqlite3.connect(db_name) as conn:
            c = conn.cursor()
            c.execute(f"SELECT password FROM {table} WHERE email = ?", (email,))
            result = c.fetchone()
            if result and result[0] == password:
                return True
            return False
    return False

# Ensure the database schema is initialized
create_db()