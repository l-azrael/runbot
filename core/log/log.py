# --coding:utf-8--
import os
import sys
import logging

from loguru import logger as _logger

from core._constants import Log
from core.path import LOG_DIR

log_path = os.path.join(LOG_DIR, Log.LOG_NAME)

_stdout_added = False
_file_added = False
_allure_added = False
_stdout_handler_id = None

_FMT_STDOUT = (
    "<green>{time:YYYY-MM-DD HH:mm:ss}</green> "
    "<m>[{process.name}]</m>-<m>[{thread.name}]</m>-"
    "<cyan>[{module}.{function}:{line}]</cyan>-"
    "<level>[{level}]</level>: <level>{message}</level>"
)
_FMT_FILE = (
    "{time:YYYY-MM-DD HH:mm:ss} "
    "[{process.name}]-[{thread.name}]-"
    "[{module}.{function}:{line}]-[{level}]: {message}"
)


class _AllureHandler(logging.Handler):
    def emit(self, record):
        logging.getLogger(record.name).handle(record)


class RunBotLogger:
    _logger = _logger

    def __init__(self, level: str = Log.DEFAULT_LEVEL):
        global _stdout_added, _file_added, _stdout_handler_id
        if not _stdout_added:
            self._logger.remove()
            _stdout_handler_id = self._logger.add(
                sys.stdout, level="INFO", format=_FMT_STDOUT
            )
            _stdout_added = True
        if not _file_added:
            self._logger.add(
                log_path, level=level.upper(),
                format=_FMT_FILE,
                rotation="10 MB",
                encoding="utf-8"
            )
            _file_added = True

    def allure_handler(self, level: str = "debug", is_processes: bool = False):
        global _allure_added
        if _allure_added:
            return
        fmt = "[{module}.{function}:{line}]-[{level}]: {message}"
        if is_processes:
            fmt = "[{process.name}]-" + fmt
        self._logger.add(_AllureHandler(), level=level.upper(), format=fmt)
        _allure_added = True

    def get_level(self, sink: str = "<stdout>") -> int:
        handlers: dict = self._logger.__dict__["_core"].__dict__["handlers"]
        for _, h in handlers.items():
            if h._name == sink:
                return h._levelno
        return 20  # 默认 INFO


runbot_logger = RunBotLogger()
logger = runbot_logger._logger
