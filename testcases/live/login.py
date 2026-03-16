# --coding:utf-8--
"""
live 模块登录实现
"""
from testcases.base_login import ModuleLogin


class LiveLogin(ModuleLogin):
    """直播模块登录"""

    def login(self) -> dict:
        # TODO: 实现实际登录逻辑
        resp_login = {}
        return resp_login

    def make_headers(self, resp_login: dict) -> dict:
        return {"token": "your_token_here"}
