# --coding:utf-8--
import jsonschema

from core.storage.schema import schema
from core.exceptions import SchemaNotFound
from core.log.log import logger


class BaseTestcase:
    """测试用例基类，提供常用断言方法"""

    def assert_eq(self, actual, expected, msg: str = ""):
        assert actual == expected, msg or f"期望 {expected!r}，实际 {actual!r}"

    def assert_neq(self, actual, expected, msg: str = ""):
        assert actual != expected, msg or f"期望不等于 {expected!r}，实际 {actual!r}"

    def assert_gt(self, actual, expected, msg: str = ""):
        assert actual > expected, msg or f"期望 > {expected}，实际 {actual}"

    def assert_lt(self, actual, expected, msg: str = ""):
        assert actual < expected, msg or f"期望 < {expected}，实际 {actual}"

    def assert_ge(self, actual, expected, msg: str = ""):
        assert actual >= expected, msg or f"期望 >= {expected}，实际 {actual}"

    def assert_le(self, actual, expected, msg: str = ""):
        assert actual <= expected, msg or f"期望 <= {expected}，实际 {actual}"

    def assert_contains(self, actual, expected, msg: str = ""):
        assert expected in actual, msg or f"期望 {actual!r} 包含 {expected!r}"

    def assert_is_none(self, actual, msg: str = ""):
        assert actual is None, msg or f"期望为 None，实际 {actual!r}"

    def assert_is_not_none(self, actual, msg: str = ""):
        assert actual is not None, msg or f"期望不为 None"

    def assert_http_code_success(self, code: int, msg: str = ""):
        assert 200 <= code < 300, msg or f"HTTP 状态码异常：{code}"

    def assert_type(self, actual, expected_type, msg: str = ""):
        assert isinstance(actual, expected_type), \
            msg or f"期望类型 {expected_type.__name__}，实际类型 {type(actual).__name__}"

    def assert_schema(self, api_name: str, response: dict):
        """从 schema 表中取出已存储的 JSON Schema 进行校验"""
        stored = schema.get(api_name)
        if stored is None:
            raise SchemaNotFound(api_name)
        try:
            jsonschema.validate(instance=response, schema=stored)
            logger.debug(f"[assert_schema] {api_name} schema 校验通过")
        except jsonschema.ValidationError as e:
            raise AssertionError(f"[assert_schema] {api_name} schema 校验失败：{e.message}")
