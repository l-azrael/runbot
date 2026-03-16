import os
import pytest

from core.fixture import ReadConfig

# 排除 _legacy 目录，避免旧用例导入报错
collect_ignore_glob = [os.path.join("testcases", "_legacy", "*")]


@pytest.fixture(scope="session", autouse=False)
def db():
    """PostgreSQL 连接 fixture（按需使用）"""
    from core.db.pg import PostgresDB
    conf = ReadConfig().get("test", "pgsql")
    if not conf:
        pytest.skip("未配置 pgsql，跳过数据库 fixture")
    instance = PostgresDB(conf)
    yield instance
    instance.close()
