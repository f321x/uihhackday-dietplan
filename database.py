import sqlite3
import time


def initialize_db():
    conn = sqlite3.connect('generations.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS users
                 (uuid TEXT PRIMARY KEY NOT NULL,
                  status INTEGER,
                  content TEXT NOT NULL,
                  time INTEGER);''')
    conn.commit()
    conn.close()


def add_row(uuid_identifier, status: int, content):
    conn = sqlite3.connect('generations.db')
    c = conn.cursor()
    c.execute("INSERT INTO users (uuid, status, content, time) VALUES (?, ?, ?, ?)",
              (uuid_identifier, status, content, int(time.time())))
    conn.commit()
    conn.close()


def delete_row(row_uuid):
    conn = sqlite3.connect('generations.db')
    c = conn.cursor()
    c.execute("DELETE FROM users WHERE uuid = ?", (row_uuid,))
    conn.commit()
    conn.close()


def fetch_row_by_uuid(row_uuid):
    conn = sqlite3.connect('generations.db')
    c = conn.cursor()
    c.execute("SELECT status, content FROM users WHERE uuid = ?", (row_uuid,))
    row = c.fetchone()
    conn.close()
    if row is None:
        return None  # Return None if no row is found
    else:
        return int(row[0]), row[1]  # Return status and content as a dictionary


def update_single_column(row_uuid, column_name, new_value):
    conn = sqlite3.connect('generations.db')
    c = conn.cursor()
    # Use parameterized query to update the specified column
    query = f"UPDATE users SET {column_name} = ? WHERE uuid = ?"
    c.execute(query, (new_value, row_uuid))
    conn.commit()
    conn.close()