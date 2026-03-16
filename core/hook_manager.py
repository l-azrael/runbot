# --coding:utf-8--
import inspect
import sys
from importlib import import_module

from core.path import BASEDIR

_hooks_loaded = False


class SessionHook:
    def __init__(self):
        self._pre_hooks = []
        self._generators = []
        self._gen_funcs = []

    def __call__(self):
        self._load_hooks()
        return self

    def _load_hooks(self):
        global _hooks_loaded
        if _hooks_loaded:
            return
        print("🚀 [RunBot] 加载 hooks...")
        sys.path.insert(0, BASEDIR)
        try:
            module = import_module("hooks")
        except ModuleNotFoundError:
            _hooks_loaded = True
            return
        for _, member in inspect.getmembers(module):
            if inspect.isfunction(member) and hasattr(member, "__wrapped__"):
                member()
        _hooks_loaded = True

    def register(self, func):
        if inspect.isgeneratorfunction(func):
            self._gen_funcs.append(func)
        else:
            self._pre_hooks.append(func)

    def execute_pre_hooks(self):
        for hook in self._pre_hooks:
            hook()
        for fn in self._gen_funcs:
            gen = fn()
            self._generators.append(gen)
            next(gen)

    def execute_post_hooks(self):
        for gen in self._generators:
            try:
                next(gen)
            except StopIteration:
                pass


session_hook = SessionHook()


def hook(func):
    """装饰器：将函数注册为 session hook"""
    from functools import wraps

    @wraps(func)
    def wrapper():
        session_hook.register(func)

    wrapper.__wrapped__ = func
    return wrapper
