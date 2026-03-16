# --coding:utf-8--
"""member 模块级 fixture"""
import pytest
from testcases.member.login import MemberLogin


@pytest.fixture(scope="module")
def member_session():
    """管理后台 session"""
    login = MemberLogin()
    return login
