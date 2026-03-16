import pytest

from apis.member.member_tag_api import DemoApi
from core.base.base_test_case import BaseTestcase
from core.fixture import ReadConfig
from core.parametrize.parametrize import parametrize_from_method
from testcases.test_factory_data.test_scenario_data.member_tag_factory import memberTagFactory
from core.log.log import logger


class TestApiTestCases(BaseTestcase):
    @pytest.fixture
    def method_fixture(self, db):
        # 创建测试资源
        conf_login = ReadConfig().get("test", "login")
        """创建一个 TestApi 实例"""
        api_instance = DemoApi(token=conf_login["web_token"], env="test")
        yield api_instance

        # 清理测试资源
        try:
            tag = db.fetch_one("mms_member_tag", {"top_shop_id": 1432176, "status": 2})
            if tag is not None:
                api_instance.api_delete_member_tag(arr=[tag["id"]])
        except Exception as e:
            logger.error(f"清理资源时出错: {e}")

    @pytest.mark.member
    @parametrize_from_method("params,desc", memberTagFactory.member_tag_data())
    def test_save_member_tag_success(self, method_fixture, db, params, desc):
        """测试成功保存成员标签"""

        # 调用测试方法
        response = method_fixture.api_save_member_tag(params)

        # 断言响应状态码为 0
        self.assert_http_code_success(response["code"])

        # 数据库数据校验示例
        params.get("name")
        user = db.fetch_one("mms_member_tag", {"top_shop_id": 1432176, "name": params.get("name")})
        self.assert_is_not_none(user)
        # if user is not None:
        #     assert user['member_id'] == 100113
        #     self.assert_eq(user['member_id'], 100113)
        #     self.assert_type(user['member_id'], int, 'member_id')
