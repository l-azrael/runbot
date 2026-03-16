import psycopg2
import yaml
from psycopg2.extras import DictCursor


class PostgresDB:
    def __init__(self, config):
        self.config = config
        self.connection = None

    def connect(self):
        """建立数据库连接"""
        if not self.connection:
            self.connection = psycopg2.connect(
                host=self.config["host"],
                port=self.config["port"],
                user=self.config["user"],
                password=self.config["password"],
                dbname=self.config["dbname"]
            )
        return self.connection

    def execute_query_cmd(self, query, params=None):
        """
        执行 SQL 查询，自动返回查询结果。
        - 如果查询返回单行，返回字典格式。
        - 如果查询返回多行，返回字典列表。
        - 如果无结果，返回 None。
        """
        try:
            with self.connect().cursor(cursor_factory=DictCursor) as cursor:
                cursor.execute(query, params or ())

                # 尝试获取结果
                result = cursor.fetchall()

                if not result:  # 无结果
                    return None
                elif len(result) == 1:  # 单行结果
                    return dict(result[0])
                else:  # 多行结果
                    return [dict(row) for row in result]
        except Exception as e:
            print(f"数据库查询出错: {e}")
            return None

    def execute_query(self, query, params=None, fetchone=False, fetchall=False):
        """执行 SQL 查询，返回字典格式"""
        with self.connect().cursor(cursor_factory=DictCursor) as cursor:
            cursor.execute(query, params or ())
            if fetchone:
                result = cursor.fetchone()
                return dict(result) if result else None
            if fetchall:
                return [dict(row) for row in cursor.fetchall()]
            self.connection.commit()

    def insert(self, table, data):
        """插入数据"""
        columns = ', '.join(data.keys())
        values_placeholder = ', '.join(['%s'] * len(data))
        query = f"INSERT INTO {table} ({columns}) VALUES ({values_placeholder}) RETURNING id"
        return self.execute_query(query, tuple(data.values()), fetchone=True)

    def fetch_one(self, table, conditions):
        """获取单条数据"""
        condition_str = " AND ".join([f"{key} = %s" for key in conditions.keys()])
        query = f"SELECT * FROM {table} WHERE {condition_str} LIMIT 1"
        return self.execute_query(query, tuple(conditions.values()), fetchone=True)

    def fetch_all(self, table, conditions=None):
        """获取多条数据"""
        if conditions:
            condition_str = " AND ".join([f"{key} = %s" for key in conditions.keys()])
            query = f"SELECT * FROM {table} WHERE {condition_str}"
            return self.execute_query(query, tuple(conditions.values()), fetchall=True)
        else:
            query = f"SELECT * FROM {table}"
            return self.execute_query(query, fetchall=True)

    def update(self, table, data, conditions):
        """更新数据"""
        set_clause = ", ".join([f"{key} = %s" for key in data.keys()])
        condition_clause = " AND ".join([f"{key} = %s" for key in conditions.keys()])
        query = f"UPDATE {table} SET {set_clause} WHERE {condition_clause}"
        self.execute_query(query, tuple(data.values()) + tuple(conditions.values()))

    def delete(self, table, conditions):
        """删除数据"""
        condition_str = " AND ".join([f"{key} = %s" for key in conditions.keys()])
        query = f"DELETE FROM {table} WHERE {condition_str}"
        self.execute_query(query, tuple(conditions.values()))

    def close(self):
        """关闭数据库连接"""
        if self.connection:
            self.connection.close()
            self.connection = None
