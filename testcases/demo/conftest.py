# --coding:utf-8--
"""demo 模块 conftest — 初始化环境配置"""
import pytest
from core.fixture import EnvVars
from core.storage.config import config
from core.storage.cache import cache


@pytest.fixture(scope="session", autouse=True)
def demo_setup():
    """自动初始化 host 和 headers 到 storage，确保直接 pytest 也能跑"""
    env = EnvVars()
    conf = env.current_env_conf
    config.set("host", conf.get("host", ""))
    config.set("current_env", env.current_env)
    # 写入空 headers（demo 不需要鉴权）
    cache.set("headers", {"Content-Type": "application/json"})
    yield
    try:
        cache.clear()
    except Exception:
        pass
