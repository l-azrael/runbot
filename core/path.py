# --coding:utf-8--
import os

BASEDIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

CONF_DIR = os.path.join(BASEDIR, "conf")
API_DIR = os.path.join(BASEDIR, "apis")
LOG_DIR = os.path.join(BASEDIR, "logs")
REPORT_DIR = os.path.join(BASEDIR, "reports")
CASE_DIR = os.path.join(BASEDIR, "testcases")
DB_DIR = os.path.join(BASEDIR, "database")
PYTEST_INI_PATH = os.path.join(BASEDIR, "pytest.ini")
RUNBOT_YAML_PATH = os.path.join(CONF_DIR, "runbot.yaml")
