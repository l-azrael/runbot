# --coding:utf-8--
import os
import shutil
import configparser
from concurrent.futures import ThreadPoolExecutor, wait, ALL_COMPLETED
from multiprocessing import Pool

import pytest

from core._constants import Allure
from core.storage.config import config
from core.fixture import SetUpSession, TearDownSession, BaseLogin
from core.hook_manager import session_hook
from core.log.log import logger, runbot_logger
from core.path import REPORT_DIR, PYTEST_INI_PATH
from core.report.html_report import ReportCollector

_allure_json_dir = os.path.join(REPORT_DIR, "json")

_RUN_MODE = {
    "Runner": "main",
    "ThreadsRunner": "mt",
    "ProcessesRunner": "mp",
}


def _session(func):
    """Session 生命周期装饰器"""
    def wrapper(self, *args, **kwargs):
        login = kwargs.get("login")
        _setup(self.__class__.__name__, login)
        try:
            result = func(self, *args, **kwargs)
        finally:
            session_hook.execute_post_hooks()
            TearDownSession().teardown()
        return result
    return wrapper


def _setup(runner_name: str, login):
    config.set("run_mode", _RUN_MODE.get(runner_name, "main"))
    SetUpSession(login).setup()
    shutil.rmtree(_allure_json_dir, ignore_errors=True)
    session_hook().execute_pre_hooks()


def _get_base_args(report_collector=None) -> list:
    args = [
        "-s",
        f"--alluredir={_allure_json_dir}",
        "--show-capture=no",
        "--log-format=%(asctime)s %(message)s",
        "--log-date-format=%Y-%m-%d %H:%M:%S",
    ]
    return args


def _get_pytest_ini_opts() -> list:
    """读取 pytest.ini 中的 addopts"""
    parser = configparser.ConfigParser()
    parser.read(PYTEST_INI_PATH, encoding="utf-8")
    try:
        opts = parser.get("pytest", "addopts")
        return opts.split() if opts else []
    except (configparser.NoSectionError, configparser.NoOptionError):
        return []


def _gen_allure(clear: bool = True):
    if not shutil.which("allure"):
        logger.info("[RunBot] 未安装 allure 命令行，跳过 allure 报告生成")
        return
    cmd = f"allure generate ./{Allure.JSON_DIR} -o ./{Allure.HTML_DIR}"
    if clear:
        cmd += " -c"
    os.system(cmd)


def _write_allure_env():
    conf = config.get_all()
    if not conf:
        return
    os.makedirs(_allure_json_dir, exist_ok=True)
    content = "\n".join(f"{k}={v}" for k, v in conf.items())
    with open(os.path.join(_allure_json_dir, "environment.properties"), "w", encoding="utf-8") as f:
        f.write(content)


def _run_pytest(args: list, plugins: list = None):
    opts = _get_pytest_ini_opts()
    logger.info(f"[RunBot] pytest 参数：{args}")
    if opts:
        logger.info(f"[RunBot] pytest.ini addopts：{opts}")
    pytest.main(args, plugins=plugins or [])


class Runner:
    def __init__(self):
        runbot_logger.allure_handler("debug")
        self._base_args = _get_base_args()
        self._report_collector = ReportCollector()

    @_session
    def run(self, args: list, login: BaseLogin = None, gen_allure: bool = True):
        """单进程运行"""
        logger.info("[RunBot] 单进程启动")
        _run_pytest(args + self._base_args, plugins=[self._report_collector])
        if gen_allure:
            _write_allure_env()
            _gen_allure()


class ThreadsRunner(Runner):
    @_session
    def run(self, task_args: list, login: BaseLogin = None,
            extra_args: list = None, gen_allure: bool = True):
        """多线程运行，task_args 为 mark 列表"""
        extra = (extra_args or []) + self._base_args
        groups = [[arg] + extra for arg in task_args]
        logger.info(f"[RunBot] 多线程启动，线程数：{len(groups)}")
        with ThreadPoolExecutor(max_workers=len(groups)) as tp:
            futures = [tp.submit(_run_pytest, g, [self._report_collector]) for g in groups]
            wait(futures, return_when=ALL_COMPLETED)
        if gen_allure:
            _write_allure_env()
            _gen_allure()


class ProcessesRunner(Runner):
    @_session
    def run(self, task_args: list, login: BaseLogin = None,
            extra_args: list = None, gen_allure: bool = True,
            process_count: int = None):
        """多进程运行"""
        runbot_logger.allure_handler("debug", is_processes=True)
        extra = (extra_args or []) + self._base_args
        groups = list([arg] + extra for arg in task_args)
        count = min(process_count or len(groups), os.cpu_count(), len(groups))
        logger.info(f"[RunBot] 多进程启动，进程数：{count}")
        with Pool(count) as pool:
            pool.map(_run_pytest, groups)
        if gen_allure:
            _write_allure_env()
            _gen_allure()
