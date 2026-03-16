# --coding:utf-8--
from functools import wraps
from typing import Callable, Union, List, Text, Dict

from jsonpath import jsonpath

from core.exceptions import JsonPathExtractFailed
from core.log.log import logger


def async_api(cycle_func: Callable, jsonpath_expr: Union[Text, List],
              expr_index: Union[int, str] = 0,
              condition: Union[Dict, bool] = None,
              *out_args, **out_kwargs):
    """
    异步接口装饰器：接口调用后从响应中提取任务 ID，传给轮询函数。

    :param cycle_func: 轮询函数
    :param jsonpath_expr: 从响应中提取异步任务 ID 的 JSONPath 表达式（支持列表）
    :param expr_index: 提取索引，传 ':' 获取整个列表
    :param condition: 执行轮询的条件，None=始终执行，bool=直接判断，
                      dict={"expr": "$.ret_code", "expected_value": 0}
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            resp = func(*args, **kwargs)
            if not _should_execute(resp, condition):
                logger.info(f"[async_api] <{func.__name__}> 不满足执行条件，跳过轮询")
                return resp

            job_id = _extract(resp, jsonpath_expr, expr_index)
            if job_id is None:
                if condition is None:
                    raise JsonPathExtractFailed(resp, jsonpath_expr)
                return resp

            logger.info(f"[async_api] <{func.__name__}> 开始轮询 <{cycle_func.__name__}>，任务ID: {job_id}")
            async_res = cycle_func(job_id, *out_args, **out_kwargs)
            if isinstance(resp, dict):
                resp.setdefault("async_res", [])
                if async_res:
                    items = async_res if isinstance(async_res, list) else [async_res]
                    resp["async_res"].extend(items)
            logger.info(f"[async_api] <{func.__name__}> 轮询完成")
            return resp
        return wrapper
    return decorator


def _extract(resp, expr, index):
    exprs = [expr] if isinstance(expr, str) else expr
    for e in exprs:
        result = jsonpath(resp, e)
        if result:
            return result if index == ":" else result[index]
    return None


def _should_execute(resp, condition) -> bool:
    if condition is None:
        return True
    if isinstance(condition, bool):
        return condition
    expr = condition.get("expr")
    expected = condition.get("expected_value")
    result = jsonpath(resp, expr)
    if result is False:
        raise JsonPathExtractFailed(resp, expr)
    return result[0] == expected
