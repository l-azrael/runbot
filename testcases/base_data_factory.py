# --coding:utf-8--
"""
测试数据工厂基类
提供常用随机数据生成方法，各模块的数据工厂继承此类。
"""
import random
import string
from typing import List


class BaseDataFactory:
    """测试数据工厂基类，提供常用随机数据生成方法"""

    @classmethod
    def data(cls) -> List[dict]:
        """子类实现，返回参数化数据列表，每条包含 desc 字段"""
        raise NotImplementedError

    @staticmethod
    def fake_str(length: int = 8) -> str:
        return "".join(random.choices(string.ascii_lowercase, k=length))

    @staticmethod
    def fake_name(prefix: str = "test_") -> str:
        return prefix + "".join(random.choices(string.ascii_lowercase, k=6))

    @staticmethod
    def fake_int(min_val: int = 1, max_val: int = 9999) -> int:
        return random.randint(min_val, max_val)

    @staticmethod
    def fake_phone() -> str:
        return "1" + str(random.randint(3, 9)) + "".join(
            random.choices(string.digits, k=9)
        )
