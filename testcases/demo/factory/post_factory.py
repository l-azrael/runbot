# --coding:utf-8--
from testcases.base_data_factory import BaseDataFactory


class PostFactory(BaseDataFactory):
    @classmethod
    def data(cls) -> list:
        return [
            {"desc": "正常请求", "name": "test_user", "age": 25},
            {"desc": "名称为空", "name": "", "age": 30},
            {"desc": "年龄边界值", "name": cls.fake_name("user_"), "age": 0},
        ]
