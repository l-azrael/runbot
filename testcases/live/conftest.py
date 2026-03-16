# --coding:utf-8--
"""live 模块级 fixture"""
import pytest
from testcases.live.login import LiveLogin


@pytest.fixture(scope="module")
def live_session():
    """直播模块 session"""
    login = LiveLogin()
    return login
