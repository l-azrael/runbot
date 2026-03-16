# --coding:utf-8--
import importlib
from functools import wraps
from typing import Text

from core.storage.cache import cache
from core.log.log import logger


def update(var_name: Text, *out_args, **out_kwargs):
    """
    后置刷新装饰器：目标接口调用后，重新调用原依赖接口刷新 cache 中的值。
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            resp = func(*args, **kwargs)
            api_info = cache.get(var_name, field="api_info")
            if api_info:
                logger.info(f"开始刷新 cache[{var_name}]")
                module = importlib.import_module(api_info["module"])
                cls_name = api_info.get("cls", "")
                method_name = api_info["name"]
                if cls_name:
                    cls = getattr(module, cls_name)
                    new_val = getattr(cls, method_name)(*out_args, **out_kwargs)
                else:
                    fn = getattr(module, method_name)
                    new_val = fn(*out_args, **out_kwargs)
                cache.update(var_name, new_val)
                logger.info(f"cache[{var_name}] 刷新完成")
            return resp
        return wrapper
    return decorator
