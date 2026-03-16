# --coding:utf-8--
from testcases.base_data_factory import BaseDataFactory


class MemberTagFactory(BaseDataFactory):
    """成员标签测试数据工厂"""

    @classmethod
    def data(cls) -> list:
        return [
            {"desc": "正常创建标签", "name": cls.fake_name("VIP_"), "type": 1},
            {"desc": "边界值-名称最长50字符", "name": "x" * 50, "type": 1},
            {"desc": "非法类型值", "name": cls.fake_name("tag_"), "type": 99},
            {"desc": "名称为空字符串", "name": "", "type": 1},
        ]

    @classmethod
    def save_data(cls) -> list:
        """仅正向用例数据（用于前置依赖）"""
        return [
            {"desc": "正常创建", "name": cls.fake_name("VIP_"), "type": 1},
        ]
