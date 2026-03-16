# --coding:utf-8--
"""
RunBot 快速上手 Demo
使用 httpbin.org 公开 API 演示框架核心用法
"""
import pytest
from core.base_testcase import BaseTestcase
from core.parametrize import parametrize
from apis.demo.apis import GetAPI, PostAPI
from apis.demo.models import PostDataRequest
from testcases.demo.factory.post_factory import PostFactory


class TestHttpbinDemo(BaseTestcase):

    @pytest.mark.demo
    def test_simple_get(self):
        """最简单的 GET 请求"""
        res = GetAPI().send()
        self.assert_http_code_success(res.status_code)
        self.assert_is_not_none(res.body)

    @pytest.mark.demo
    @parametrize(PostFactory.data())
    def test_post_with_factory(self, data):
        """POST 请求 — 工厂类驱动参数化"""
        body = PostDataRequest(name=data["name"], age=data["age"])
        res = PostAPI(request_body=body).send()
        self.assert_http_code_success(res.status_code)
        # httpbin 会把请求体原样返回在 json 字段里
        self.assert_eq(res.body["json"]["name"], data["name"])
        self.assert_eq(res.body["json"]["age"], data["age"])

    @pytest.mark.demo
    @parametrize("testcases/demo/data/post_data.json")
    def test_post_with_json_file(self, data):
        """POST 请求 — JSON 文件驱动参数化"""
        body = PostDataRequest(name=data["name"], age=data["age"])
        res = PostAPI(request_body=body).send()
        self.assert_http_code_success(res.status_code)
        self.assert_eq(res.body["json"]["name"], data["name"])
        self.assert_eq(res.body["json"]["age"], data["age"])

    @pytest.mark.demo
    @parametrize([
        {"desc": "内联数据-正常", "name": "inline_user", "age": 18},
        {"desc": "内联数据-大龄", "name": "old_user", "age": 99},
    ])
    def test_post_inline(self, data):
        """POST 请求 — 内联数据驱动"""
        body = PostDataRequest(name=data["name"], age=data["age"])
        res = PostAPI(request_body=body).send()
        self.assert_http_code_success(res.status_code)
        self.assert_contains(res.body["url"], "/post")
