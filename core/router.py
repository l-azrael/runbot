# --coding:utf-8--
from typing import Callable

ROUTE_META_ATTR = "__runbot_route__"


class Router:
    """路由装饰器，给接口类打上 method + path 元数据"""

    def _register(self, method: str, path: str) -> Callable:
        def decorator(cls):
            setattr(cls, ROUTE_META_ATTR, {"method": method.upper(), "path": path})
            return cls
        return decorator

    def get(self, path: str) -> Callable:
        return self._register("GET", path)

    def post(self, path: str) -> Callable:
        return self._register("POST", path)

    def put(self, path: str) -> Callable:
        return self._register("PUT", path)

    def delete(self, path: str) -> Callable:
        return self._register("DELETE", path)

    def patch(self, path: str) -> Callable:
        return self._register("PATCH", path)


router = Router()
