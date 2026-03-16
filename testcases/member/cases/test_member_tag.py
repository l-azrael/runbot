# --coding:utf-8--
"""
成员标签接口测试用例
演示 RunBot 框架标准用法：
  - BaseAPIObject 声明式接口调用
  - @parametrize 统一参数化（类驱动 / 内联 / 文件驱动）
  - BaseTestcase 断言方法
  - @dependence 前置依赖
"""
import pytest

from core.base_testcase import BaseTestcase
from core.parametrize import parametrize
from apis.member.apis import SaveMemberTagAPI, DeleteMemberTagAPI
from apis.member.models import SaveMemberTagAPIRequest, DeleteMemberTagAPIRequest
from testcases.member.factory.member_tag_factory import MemberTagFactory


class TestMemberTag(BaseTestcase):

    # ------------------------------------------------------------------ 正向用例
    @pytest.mark.member
    @parametrize(MemberTagFactory.data())
    def test_save_member_tag(self, data):
        """保存成员标签 — 工厂类驱动"""
        body = SaveMemberTagAPIRequest(name=data["name"], type=data["type"])
        res = SaveMemberTagAPI(request_body=body).send()
        # 正向用例期望 code=0，非法参数期望非 0
        if data.get("type") == 1 and data.get("name"):
            self.assert_eq(res.body.get("code"), 0)
        else:
            self.assert_is_not_none(res.body.get("code"))

    # ------------------------------------------------------------------ 内联驱动
    @pytest.mark.member
    @parametrize([
        {"desc": "删除存在的标签", "ids": [1001]},
        {"desc": "删除不存在的标签", "ids": [9999]},
    ])
    def test_delete_member_tag(self, data):
        """删除成员标签 — 内联数据驱动"""
        body = DeleteMemberTagAPIRequest(ids=data["ids"])
        res = DeleteMemberTagAPI(request_body=body).send()
        self.assert_is_not_none(res.body)

    # ------------------------------------------------------------------ 文件驱动
    @pytest.mark.member
    @parametrize("testcases/member/data/member_tag_cases.json")
    def test_save_member_tag_from_file(self, data):
        """保存成员标签 — JSON 文件驱动"""
        body = SaveMemberTagAPIRequest(name=data["name"], type=data["type"])
        res = SaveMemberTagAPI(request_body=body).send()
        self.assert_eq(res.body.get("code"), data.get("expected_code", 0))
