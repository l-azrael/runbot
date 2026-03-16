# --coding:utf-8--
import json
import sqlite3
from multiprocessing import current_process
from threading import current_thread

from jsonpath import jsonpath

from core.storage.db import SQLiteDB
from core._constants import DataBase
from core.exceptions import JsonPathExtractFailed


def _get_worker() -> str:
    from core.storage.config import config
    run_mode = config.get("run_mode") or "main"
    if run_mode == "mt":
        return current_thread().name
    if run_mode == "mp":
        return current_process().name
    return "MainProcess"


class Cache(SQLiteDB):
    def __init__(self):
        super().__init__()
        self.table = DataBase.CACHE_TABLE

    def set(self, key: str, value, api_info=None):
        if self.get(key) is not None:
            return
        worker = _get_worker()
        val = json.dumps(value, ensure_ascii=False)
        if api_info:
            self.execute_sql(
                f"INSERT INTO {self.table}(var_name, response, worker, api_info) VALUES (?,?,?,?)",
                (key, val, worker, json.dumps(api_info, ensure_ascii=False))
            )
        else:
            self.execute_sql(
                f"INSERT INTO {self.table}(var_name, response, worker) VALUES (?,?,?)",
                (key, val, worker)
            )

    def update(self, key: str, value):
        worker = _get_worker()
        self.update_data(
            self.table,
            {"response": json.dumps(value, ensure_ascii=False)},
            {"var_name": key, "worker": worker}
        )

    def get(self, key: str, field: str = "response"):
        if key == "headers":
            rows = self.query_sql(
                f"SELECT {field} FROM {self.table} WHERE var_name=?", (key,)
            )
        else:
            worker = _get_worker()
            rows = self.query_sql(
                f"SELECT {field} FROM {self.table} WHERE var_name=? AND worker=?",
                (key, worker)
            )
        if not rows:
            return None
        return json.loads(rows[0][0])

    def get_by_jsonpath(self, key: str, expr: str, index: int = 0):
        data = self.get(key)
        result = jsonpath(data, expr)
        if result is False:
            raise JsonPathExtractFailed(data, expr)
        return result[index]

    def clear(self):
        self.execute_sql(f"DELETE FROM {self.table}")


cache = Cache()
