# --coding:utf-8--
from tenacity import (
    retry, stop_after_attempt, wait_fixed,
    retry_if_exception_type, retry_if_result, Retrying
)


def make_retry(counts: int = 3, interval: float = 2, retry_condition=None, exception_type=Exception):
    """
    返回 tenacity retry 装饰器。
    retry_condition: callable，接收返回值，返回 True 时重试（业务级）
    exception_type: 异常类型，抛出该异常时重试（HTTP级）
    """
    retry_kwargs = dict(
        stop=stop_after_attempt(counts),
        wait=wait_fixed(interval),
        reraise=True,
    )
    if retry_condition:
        retry_kwargs["retry"] = retry_if_result(retry_condition)
    else:
        retry_kwargs["retry"] = retry_if_exception_type(exception_type)
    return retry(**retry_kwargs)


class Retry:
    """代码片段级重试，用法：for attempt in Retry(...): with attempt: ..."""

    def __init__(self, counts: int = 3, interval: float = 2, exception_type=Exception):
        self._retrying = Retrying(
            stop=stop_after_attempt(counts),
            wait=wait_fixed(interval),
            retry=retry_if_exception_type(exception_type),
            reraise=True,
        )

    def __iter__(self):
        return self._retrying.__iter__()
