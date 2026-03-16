# --coding:utf-8--
"""
代码生成器：将解析后的 APIDef 列表渲染为 apis.py + models.py
"""
import os
from typing import Optional

from jinja2 import Environment, FileSystemLoader

from core.maker.openapi_parser import OpenAPIParser, APIDef, ModelDef

_TEMPLATE_DIR = os.path.join(os.path.dirname(__file__), "templates")


def _get_env() -> Environment:
    env = Environment(
        loader=FileSystemLoader(_TEMPLATE_DIR),
        trim_blocks=True,
        lstrip_blocks=True,
    )
    import json
    env.filters["tojson"] = lambda v: json.dumps(v, ensure_ascii=False)
    return env


def _collect_models(apis: list[APIDef]) -> list[ModelDef]:
    seen = set()
    models = []
    for api in apis:
        for m in (api.request_model, api.response_model):
            if m and m.name not in seen:
                seen.add(m.name)
                models.append(m)
    return models


def _module_path_from_output(output_dir: str) -> str:
    """将输出目录路径转换为 Python 模块路径，如 apis/member -> apis.member
    只取相对于项目根目录的部分，绝对路径也能处理。
    """
    from core.path import BASEDIR
    # 转为绝对路径后取相对路径
    abs_out = os.path.abspath(output_dir)
    try:
        rel = os.path.relpath(abs_out, BASEDIR)
    except ValueError:
        # Windows 跨盘符时 relpath 会报错，直接用目录名
        rel = os.path.basename(abs_out)
    return rel.replace(os.sep, ".").replace("/", ".")


def generate(spec_source: str, output_dir: str,
             tag_filter: Optional[str] = None,
             path_filter: Optional[str] = None):
    """
    主入口：解析 spec，生成 apis.py + models.py 到 output_dir

    :param spec_source: OpenAPI 文档路径或 URL
    :param output_dir:  输出目录，如 apis/member
    :param tag_filter:  只生成指定 tag 的接口
    :param path_filter: 只生成路径以此前缀开头的接口
    """
    parser = OpenAPIParser(spec_source)
    apis = parser.parse(tag_filter=tag_filter, path_filter=path_filter)

    if not apis:
        print(f"[RunBot maker] 未找到匹配的接口（tag={tag_filter}, path={path_filter}）")
        return

    models = _collect_models(apis)
    imports = [m.name for m in models]
    module_path = _module_path_from_output(output_dir)

    os.makedirs(output_dir, exist_ok=True)
    jinja = _get_env()

    # 生成 models.py
    models_tpl = jinja.get_template("models_template.j2")
    models_code = models_tpl.render(models=models)
    _write(os.path.join(output_dir, "models.py"), models_code)

    # 生成 apis.py
    apis_tpl = jinja.get_template("apis_template.j2")
    apis_code = apis_tpl.render(apis=apis, imports=imports, module_path=module_path)
    _write(os.path.join(output_dir, "apis.py"), apis_code)

    # 确保 __init__.py 存在
    init_path = os.path.join(output_dir, "__init__.py")
    if not os.path.exists(init_path):
        _write(init_path, "")

    print(f"[RunBot maker] 生成完成 → {output_dir}/")
    print(f"  接口数：{len(apis)}，模型数：{len(models)}")


def _write(path: str, content: str):
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)
    print(f"  写入：{path}")
