import pytest

from core.base.base_test_case import BaseTestcase
from core.parametrize.custom_parametrize_from_file import custom_parametrize_from_file


class TestParametrizeFileDemo(BaseTestcase):
    @pytest.mark.member
    @custom_parametrize_from_file("test_parametrize_file_demo.json")
    def test_read_parametrize_json_test(self, params):
        print(f"Params: {params}")
        # self.assert_eq(200, result.code)
