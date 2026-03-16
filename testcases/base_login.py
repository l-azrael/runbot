# --coding:utf-8--
"""
模块级登录基类
各业务模块继承此类，实现自己的登录逻辑和 headers 构造。
"""
from core.fixture import BaseLogin


class ModuleLogin(BaseLogin):
    """模块级登录基类，各模块继承后实现自己的登录逻辑"""

    def login(self) -> dict:
        raise NotImplementedError

    def make_headers(self, resp_login: dict) -> dict:
        raise NotImplementedError

    # ---- 通用工具方法 ----

    def _request_token(self, url: str, payload: dict) -> str:
        """通用的 token 请求封装"""
        import requests
        resp = requests.post(url, json=payload)
        resp.raise_for_status()
        return resp.json().get("token", "")

    def _build_bearer_headers(self, token: str) -> dict:
        """构造 Bearer Token headers"""
        return {"Authorization": f"Bearer {token}"}
