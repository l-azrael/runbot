import os
import requests
from jinja2 import Environment, FileSystemLoader

from app.generateapiscode.get_project_interfaces import get_project_interfaces

import re


def camel_to_snake(name):
    """
    将驼峰命名转换为下划线命名
    - 例如：liveId -> live_id
    - 例如：getLiveList -> get_live_list
    """
    # 使用正则表达式插入下划线
    name = re.sub(r'(?<!^)([A-Z])', r'_\1', name)
    # 转换为小写
    return name.lower()


def parse_interface(interface):
    """
    解析单个接口数据
    """
    return {
        "path": interface.get("path"),
        "method": interface.get("method"),
        "title": interface.get("title"),
        "req_body_other": interface.get("req_body_other", "{}"),
        "req_query": interface.get("req_query", []),
        "res_body": interface.get("res_body", "{}")
    }


def extract_first_part(path):
    """
    提取路径的第一部分
    """
    path = path.replace("{", "").replace("}", "")
    parts = path.strip("/").split("/")
    return parts[0]


def extract_remaining_part(path):
    """
    提取路径的剩余部分
    - 如果路径只有一部分（如 `/live`），返回该部分（如 `live`）。
    - 如果路径有多部分（如 `/live/list` 或 `/live/list/search`），返回最后两部分并用下划线连接（如 `list` 或 `list_search`）。
    - 如果路径部分是驼峰命名（如 `liveId`），转换为下划线命名（如 `live_id`）。
    """
    # 去掉路径中的 { 和 }
    path = path.replace("{", "").replace("}", "")
    # 去掉开头的 /，然后按 / 分割
    parts = path.strip("/").split("/")

    if len(parts) == 1:
        # 如果路径只有一部分，返回该部分（转换为下划线命名）
        return camel_to_snake(parts[0])
    else:
        # 如果路径有多部分，返回最后两部分并用下划线连接（转换为下划线命名）
        return "_".join(camel_to_snake(part) for part in parts[-2:])


def generate_api_code(apis, api_endpoint_dir=r'D:\AutoTest\QGAutoDemo\apis\eshop1\api',
                      api_class_dir=r'D:\AutoTest\QGAutoDemo\apis\eshop1'):
    """
    生成 API 定义代码和 API 类文件
    """
    # 设置模板环境
    env = Environment(loader=FileSystemLoader("templates"))

    # 加载模板
    api_endpoint_template = env.get_template("api_endpoint_template.j2")
    api_class_template = env.get_template("api_class_template.j2")

    if not os.path.exists(api_endpoint_dir):
        os.makedirs(api_endpoint_dir)

    # 提取路径的第一部分
    first_part = extract_first_part(apis[0]["path"]) if apis else "default"
    class_name = first_part.capitalize() + "ApiPath"
    api_class_name = "Api" + first_part.capitalize()

    # 准备模板数据
    template_data = {
        "class_name": class_name,
        "api_class_name": api_class_name,
        "first_part": first_part,
        "apis": []
    }

    for api in apis:
        # 提取路径的剩余部分
        remaining_part = extract_remaining_part(api["path"])

        # 生成常量名和方法名
        constant_name = api["method"].upper() + "_" + remaining_part.upper()
        method_name = "api_" + api["method"].lower() + "_" + remaining_part.lower()

        # 添加到模板数据
        template_data["apis"].append({
            "constant_name": constant_name,
            "method_name": method_name,
            "path": api["path"],
            "method": api["method"],
            "title": api["title"]
        })

    # 生成 API 定义文件
    api_endpoint_content = api_endpoint_template.render(template_data)
    api_definition_filename = f"{first_part}_api.py"
    api_definition_filepath = os.path.join(api_endpoint_dir, api_definition_filename)
    with open(api_definition_filepath, "w", encoding="utf-8") as f:
        f.write(api_endpoint_content)

    # 生成 API 类文件
    api_class_content = api_class_template.render(template_data)
    api_class_filename = f"api_service_{first_part}.py"
    api_class_filepath = os.path.join(api_class_dir, api_class_filename)
    with open(api_class_filepath, "w", encoding="utf-8") as f:
        f.write(api_class_content)

    print(f"API 定义代码和 API 类文件生成完成，保存到目录: {api_class_dir}")


def main():
    # 获取接口数据
    project_id = 491  # 你的项目 ID
    interfaces = get_project_interfaces(project_id)

    # 解析接口数据
    apis = [parse_interface(interface) for interface in interfaces]

    # 生成 API 定义代码和 API 类文件
    generate_api_code(apis)


if __name__ == "__main__":
    main()
