# --coding:utf-8--
import os
import sqlite3
import threading

from core._constants import DataBase
from core.path import DB_DIR

DB_PATH = os.path.join(DB_DIR, DataBase.DB_NAME)
_lock = threading.RLock()


def _init_db(conn: sqlite3.Connection):
    """初始化数据库表结构"""
    conn.executescript("""
        CREATE TABLE IF NOT EXISTS config (
            key   TEXT PRIMARY KEY,
            value TEXT NOT NULL
        );
        CREATE TABLE IF NOT EXISTS cache (
            var_name TEXT NOT NULL,
            response TEXT NOT NULL,
            worker   TEXT NOT NULL,
            api_info TEXT,
            PRIMARY KEY (var_name, worker)
        );
        CREATE TABLE IF NOT EXISTS schema (
            api_name TEXT PRIMARY KEY,
            schema   TEXT NOT NULL
        );
    """)
    conn.commit()


class SQLiteDB:
    def __init__(self, db_path: str = DB_PATH):
        self.connection = sqlite3.connect(db_path, check_same_thread=False)
        _init_db(self.connection)
        self.cursor = self.connection.cursor()

    def close(self):
        self.connection.close()

    def execute_sql(self, sql: str, params=None):
        with _lock:
            self.cursor.execute(sql, params or ())
            self.connection.commit()

    def query_sql(self, sql: str, params=None) -> list:
        with _lock:
            rows = self.cursor.execute(sql, params or ())
            return list(rows)

    def select_data(self, table: str) -> list:
        return self.query_sql(f"SELECT * FROM {table}")

    def update_data(self, table: str, data: dict, where: dict):
        set_clause = ", ".join(f"{k}=?" for k in data)
        where_clause = " AND ".join(f"{k}=?" for k in where)
        sql = f"UPDATE {table} SET {set_clause} WHERE {where_clause}"
        self.execute_sql(sql, list(data.values()) + list(where.values()))
