# --coding:utf-8--

class DataBase:
    DB_NAME = "runbot.db"
    CONFIG_TABLE = 'config'
    CACHE_TABLE = 'cache'
    SCHEMA_TABLE = 'schema'


class Log:
    LOG_NAME = "log.log"
    DEFAULT_LEVEL = "debug"


class Conf:
    CONF_NAME = "config.yaml"
    CURRENT_ENV_KEY = 'current_env'


class Allure:
    JSON_DIR = "reports/json"
    HTML_DIR = "reports/html"
