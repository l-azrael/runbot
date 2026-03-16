# --coding:utf-8--
import time
from typing import Callable

from core.middlewares.base import middleware
from core.log.log import logger

_DEFAULT_RETRY_CODES = {500, 502, 503, 504}
_MAX_RETRIES = 3
_INTERVAL = 2


@middleware(name="retry", priority=800)
def retry_mw(request: dict, call_next: Callable) -> dict:
    """HTTP 状态码异常时自动重试（仅对 5xx 生效）"""
    if not request.get("_http_retry", False):
        return call_next(request)

    counts = request.get("_retry_counts", _MAX_RETRIES)
    interval = request.get("_retry_interval", _INTERVAL)
    retry_codes = set(request.get("_retry_codes", _DEFAULT_RETRY_CODES))

    for attempt in range(1, counts + 1):
        response = call_next(request)
        status = response.get("status_code", 200)
        if status not in retry_codes:
            return response
        if attempt < counts:
            logger.warning(f"[retry_mw] 状态码 {status}，第 {attempt} 次重试，等待 {interval}s")
            time.sleep(interval)

    return response
