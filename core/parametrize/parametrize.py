# --coding:utf-8--
import json
import os
from typing import Union, List

import pytest
import yaml

from core.path import BASEDIR


def parametrize(data: Union[str, list]):
    """
    统一参数化装饰器，支持三种驱动方式：
    - 文件驱动：传入 JSON/YAML 文件路径（相对项目根目录）
    - 类驱动：传入工厂类返回的 list
    - 内联驱动：直接传入 list

    数据格式统一为 list[dict]，其中 desc 字段自动作为用例 ID。
    """
    dataset = _load(data)
    ids = [str(item.get("desc", i)) for i, item in enumerate(dataset)]
    return pytest.mark.parametrize("data", dataset, ids=ids)


def _load(data: Union[str, list]) -> List[dict]:
    if isinstance(data, list):
        return data

    if isinstance(data, str):
        path = data if os.path.isabs(data) else os.path.join(BASEDIR, data)
        if not os.path.exists(path):
            raise FileNotFoundError(f"参数化数据文件未找到：{path}")
        with open(path, encoding="utf-8") as f:
            if path.endswith(".json"):
                return json.load(f)
            elif path.endswith((".yaml", ".yml")):
                return yaml.safe_load(f)
            else:
                raise ValueError(f"不支持的数据文件格式：{path}，仅支持 .json / .yaml")

    raise TypeError(f"parametrize 参数类型错误：{type(data)}，应为 str 或 list")
