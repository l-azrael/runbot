# coding=utf-8
class TestDemoData:
    user_token = 's-web-f0da50acfe19dd06a290648d88d13b2e'

    @staticmethod
    def demo_data():
        params = [
            {"params": {"selectAll": "false"}, "desc": "描述信息"},
            {"params": {"selectAll": "false"}, "desc": "描述信息1"},
            {"params": {"selectAll": "false"}, "desc": "描述信息2"},
            {"params": {"selectAll": "false"}, "desc": "描述信息2"},
        ]
        return params

    @staticmethod
    def demo_data_test():
        params = [
            {"selectAll": "false", "desc": "描述信息"},
            {"selectAll": "false", "desc": "描述信息2"},
            {"selectAll": "false", "desc": "描述信息3"},
            {"selectAll": "false", "desc": "描述信息4"},
        ]
        return params


testDemoData = TestDemoData()
