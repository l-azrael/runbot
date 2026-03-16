import uuid


class memberTagFactory:

    @staticmethod
    def member_tag_data():
        random_string = str(uuid.uuid4())[:4]
        name = f"VIP{random_string}"
        params = [
            {"params": {"name": name, "type": 1}, "desc": "正常创建"},
            {"params": {"name": name, "type": 0}, "desc": "创建失败"}
        ]
        return params
