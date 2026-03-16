# --coding:utf-8--
import json
import sqlite3

from core.storage.db import SQLiteDB
from core._constants import DataBase


class Config(SQLiteDB):
    def __init__(self):
        super().__init__()
        self.table = DataBase.CONFIG_TABLE

    def set(self, key: str, value):
        val = json.dumps(value, ensure_ascii=False)
        try:
            self.execute_sql(
                f"INSERT INTO {self.table}(key, value) VALUES (?, ?)", (key, val)
            )
        except sqlite3.IntegrityError:
            self.execute_sql(
                f"UPDATE {self.table} SET value=? WHERE key=?", (val, key)
            )

    def get(self, key: str):
        rows = self.query_sql(f"SELECT value FROM {self.table} WHERE key=?", (key,))
        if not rows:
            return None
        return json.loads(rows[0][0])

    def get_all(self) -> dict:
        rows = self.select_data(self.table)
        return {row[0]: json.loads(row[1]) for row in rows}

    def clear(self):
        self.execute_sql(f"DELETE FROM {self.table}")


config = Config()
