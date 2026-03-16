# --coding:utf-8--
"""
member 模块登录实现
"""
from testcases.base_login import ModuleLogin


class MemberLogin(ModuleLogin):
    """管理后台登录"""

    def login(self) -> dict:
        # TODO: 实现实际登录逻辑
        resp_login = {}
        return resp_login

    def make_headers(self, resp_login: dict) -> dict:
        return {"token": "your_token_here"}
