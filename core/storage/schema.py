# --coding:utf-8--
import json
import sqlite3

from core.storage.db import SQLiteDB
from core._constants import DataBase


class Schema(SQLiteDB):
    def __init__(self):
        super().__init__()
        self.table = DataBase.SCHEMA_TABLE

    def set(self, key: str, value):
        try:
            self.execute_sql(
                f"INSERT INTO {self.table}(api_name, schema) VALUES (?,?)",
                (key, json.dumps(value, ensure_ascii=False))
            )
        except sqlite3.IntegrityError:
            pass  # schema 只写一次，重复忽略

    def get(self, key: str):
        rows = self.query_sql(
            f"SELECT schema FROM {self.table} WHERE api_name=?", (key,)
        )
        if not rows:
            return None
        return json.loads(rows[0][0])

    def clear(self):
        self.execute_sql(f"DELETE FROM {self.table}")


schema = Schema()
