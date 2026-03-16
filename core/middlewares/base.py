# --coding:utf-8--
from typing import Callable, List

_registry: List[dict] = []


def middleware(name: str, priority: int = 500, enabled: bool = True):
    """注册中间件装饰器，priority 越大越先执行"""
    def decorator(fn: Callable):
        if enabled:
            _registry.append({"name": name, "priority": priority, "fn": fn})
            _registry.sort(key=lambda x: x["priority"], reverse=True)
        fn._middleware_name = name
        return fn
    return decorator


class MiddlewareChain:
    """构建并执行中间件链"""

    def __init__(self, send_fn: Callable):
        self._send_fn = send_fn

    def execute(self, request: dict) -> dict:
        chain = list(_registry)  # 当前已注册的中间件快照

        def call_next(req, index=0):
            if index >= len(chain):
                return self._send_fn(req)
            mw = chain[index]
            return mw["fn"](req, lambda r: call_next(r, index + 1))

        return call_next(request)
