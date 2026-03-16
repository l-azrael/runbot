# --coding:utf-8--
import importlib
from functools import wraps
from typing import Callable, Text, Union

from core.storage.cache import cache
from core.log.log import logger


def dependence(dependent_api: Union[Callable, str], var_name: Text,
               imp_module: str = None, *out_args, **out_kwargs):
    """
    前置依赖装饰器：在目标接口调用前先调用依赖接口，结果存入 cache。
    若 var_name 已存在则跳过调用。

    :param dependent_api: 依赖接口，可传入可调用对象或 "ClassName.method_name" 字符串
    :param var_name: 存入 cache 的 key
    :param imp_module: 当 dependent_api 为字符串时，需要指定模块路径（如 "apis.member.member_tag_api"）
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            if cache.get(var_name) is None:
                res, api_info = _call_dependent(dependent_api, func.__name__, imp_module, *out_args, **out_kwargs)
                cache.set(var_name, res, api_info=api_info)
                logger.info(f"依赖 <{api_info.get('name')}> 执行完成，结果已存入 cache[{var_name}]")
            else:
                logger.info(f"cache[{var_name}] 已存在，跳过依赖调用")
            return func(*args, **kwargs)
        return wrapper
    return decorator


def _call_dependent(dependent_api, caller_name, imp_module, *args, **kwargs):
    if isinstance(dependent_api, str):
        cls_name, method_name = dependent_api.split(".")
        module = importlib.import_module(imp_module)
        cls = getattr(module, cls_name)
        res = getattr(cls, method_name)(*args, **kwargs)
        api_info = {"name": method_name, "module": imp_module, "cls": cls_name.lower()}
    else:
        res = dependent_api(*args, **kwargs)
        name = dependent_api.__name__
        module_name = dependent_api.__module__
        api_info = {"name": name, "module": module_name, "cls": ""}
    return res, api_info
