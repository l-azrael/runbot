# --coding:utf-8--
import os
from abc import ABCMeta, abstractmethod

import yaml

from core._constants import Conf
from core.storage.config import config
from core.storage.cache import cache
from core.exceptions import ConfKeyError
from core.path import CONF_DIR


class ReadConfig:
    """单例配置读取器，支持多环境，支持 RUNBOT_ENV 环境变量覆盖"""
    _instance = None
    _data = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._load()
        return cls._instance

    def _load(self):
        path = os.path.join(CONF_DIR, Conf.CONF_NAME)
        with open(path, encoding="utf-8") as f:
            self._data = yaml.safe_load(f)

    def get(self, *keys):
        cur = self._data
        for k in keys:
            if isinstance(cur, dict):
                cur = cur.get(k)
            else:
                return None
        return cur


class EnvVars:
    def __init__(self):
        self._conf = ReadConfig()

    @property
    def current_env(self) -> str:
        # 环境变量优先级最高
        env = os.environ.get("RUNBOT_ENV") or self._conf.get(Conf.CURRENT_ENV_KEY)
        if not env:
            raise ConfKeyError(Conf.CURRENT_ENV_KEY)
        return env

    @property
    def current_env_conf(self) -> dict:
        conf = self._conf.get(self.current_env)
        if not conf:
            raise ConfKeyError(self.current_env)
        return conf


class BaseLogin(metaclass=ABCMeta):
    env_vars = EnvVars()

    def __init__(self):
        self.host = self.env_vars.current_env_conf.get("host")
        self.account = self.env_vars.current_env_conf.get("account")
        self.current_env = self.env_vars.current_env

    @abstractmethod
    def login(self):
        pass

    @abstractmethod
    def make_headers(self, resp_login: dict) -> dict:
        pass


class SetUpSession:
    def __init__(self, login_obj=None):
        self.login_obj = login_obj

    def setup(self):
        env = EnvVars()
        # 写入全局配置
        config.set("current_env", env.current_env)
        for k, v in env.current_env_conf.items():
            config.set(k, v)
        # 写入 headers
        headers = {}
        if self.login_obj:
            resp = self.login_obj.login()
            headers = self.login_obj.make_headers(resp)
        cache.set("headers", headers)


class TearDownSession:
    def teardown(self):
        cache.clear()
        cache.close()
        config.close()
