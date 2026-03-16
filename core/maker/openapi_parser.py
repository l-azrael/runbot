# --coding:utf-8--
"""
OpenAPI/Swagger 文档解析器
支持从 URL 或本地文件加载，支持按 tag / path 前缀过滤
"""
import json
import re
from typing import Optional
from urllib.parse import urlparse

import requests
import yaml


# 类型映射：OpenAPI type -> Python type hint
_TYPE_MAP = {
    ("string", None): "str",
    ("integer", None): "int",
    ("integer", "int32"): "int",
    ("integer", "int64"): "int",
    ("number", None): "float",
    ("number", "float"): "float",
    ("number", "double"): "float",
    ("boolean", None): "bool",
    ("array", None): "list",
    ("object", None): "dict",
}


def _oa_type(schema: dict) -> str:
    t = schema.get("type", "object")
    fmt = schema.get("format")
    return _TYPE_MAP.get((t, fmt), _TYPE_MAP.get((t, None), "Any"))


def _to_class_name(s: str) -> str:
    """camelCase / snake_case / kebab-case -> PascalCase"""
    # 先把 camelCase 拆开：saveMemberTag -> save_Member_Tag
    s = re.sub(r"([a-z\d])([A-Z])", r"\1_\2", s)
    s = re.sub(r"[^a-zA-Z0-9]+", "_", s)
    return "".join(w.capitalize() for w in s.split("_") if w)


def _to_snake(s: str) -> str:
    s = re.sub(r"[^a-zA-Z0-9]+", "_", s)
    s = re.sub(r"([A-Z]+)([A-Z][a-z])", r"\1_\2", s)
    s = re.sub(r"([a-z\d])([A-Z])", r"\1_\2", s)
    return s.lower().strip("_")


class FieldDef:
    def __init__(self, name: str, type_hint: str, required: bool,
                 description: str = "", example=None, enum: list = None):
        self.name = name
        self.type_hint = type_hint
        self.required = required
        self.description = description
        self.example = example
        self.enum = enum or []


class ModelDef:
    def __init__(self, name: str, fields: list[FieldDef], description: str = ""):
        self.name = name
        self.fields = fields
        self.description = description


class APIDef:
    def __init__(self, class_name: str, method: str, path: str,
                 summary: str, tag: str,
                 request_model: Optional[ModelDef],
                 response_model: Optional[ModelDef]):
        self.class_name = class_name
        self.method = method
        self.path = path
        self.summary = summary
        self.tag = tag
        self.request_model = request_model
        self.response_model = response_model


class OpenAPIParser:
    def __init__(self, spec_source: str):
        self._spec = self._load(spec_source)
        self._components = self._spec.get("components", {}).get("schemas", {})
        # Swagger 2.x
        if not self._components:
            self._components = self._spec.get("definitions", {})

    # ------------------------------------------------------------------ load
    def _load(self, source: str) -> dict:
        parsed = urlparse(source)
        if parsed.scheme in ("http", "https"):
            resp = requests.get(source, timeout=15)
            resp.raise_for_status()
            try:
                return resp.json()
            except Exception:
                return yaml.safe_load(resp.text)
        with open(source, encoding="utf-8") as f:
            if source.endswith((".yaml", ".yml")):
                return yaml.safe_load(f)
            return json.load(f)

    # ------------------------------------------------------------------ parse
    def parse(self, tag_filter: Optional[str] = None,
              path_filter: Optional[str] = None) -> list[APIDef]:
        paths = self._spec.get("paths", {})
        result = []
        for path, path_item in paths.items():
            if path_filter and not path.startswith(path_filter):
                continue
            for method, op in path_item.items():
                if method.upper() not in ("GET", "POST", "PUT", "DELETE", "PATCH"):
                    continue
                tags = op.get("tags", ["default"])
                if tag_filter and tag_filter not in tags:
                    continue
                api_def = self._parse_operation(method, path, op, tags[0])
                result.append(api_def)
        return result

    def _parse_operation(self, method: str, path: str, op: dict, tag: str) -> APIDef:
        summary = op.get("summary", "") or op.get("operationId", "")
        op_id = op.get("operationId") or f"{method}_{path}"
        class_name = _to_class_name(op_id) + "API"

        request_model = self._parse_request(op, class_name)
        response_model = self._parse_response(op, class_name)

        return APIDef(
            class_name=class_name,
            method=method.upper(),
            path=path,
            summary=summary,
            tag=tag,
            request_model=request_model,
            response_model=response_model,
        )

    def _parse_request(self, op: dict, class_name: str) -> Optional[ModelDef]:
        # OpenAPI 3.x requestBody
        req_body = op.get("requestBody", {})
        content = req_body.get("content", {})
        schema = None
        for mime, media in content.items():
            schema = media.get("schema")
            break

        # Swagger 2.x body parameter
        if schema is None:
            for param in op.get("parameters", []):
                if param.get("in") == "body":
                    schema = param.get("schema")
                    break

        if schema is None:
            return None

        fields = self._schema_to_fields(schema, op.get("requestBody", {}).get("required", False))
        if not fields:
            return None
        return ModelDef(name=f"{class_name}Request", fields=fields)

    def _parse_response(self, op: dict, class_name: str) -> Optional[ModelDef]:
        responses = op.get("responses", {})
        schema = None
        for code in ("200", "201", "default"):
            resp = responses.get(code, {})
            content = resp.get("content", {})
            for mime, media in content.items():
                schema = media.get("schema")
                break
            # Swagger 2.x
            if schema is None and "schema" in resp:
                schema = resp["schema"]
            if schema:
                break

        if schema is None:
            return None

        fields = self._schema_to_fields(schema, required=False)
        if not fields:
            return None
        return ModelDef(name=f"{class_name}Response", fields=fields)

    def _schema_to_fields(self, schema: dict, required=False) -> list[FieldDef]:
        # resolve $ref
        schema = self._resolve_ref(schema)
        props = schema.get("properties", {})
        required_fields = set(schema.get("required", []))
        fields = []
        for name, prop in props.items():
            prop = self._resolve_ref(prop)
            type_hint = _oa_type(prop)
            if not prop.get("required", False) and name not in required_fields:
                type_hint = f"Optional[{type_hint}]"
            fields.append(FieldDef(
                name=_to_snake(name),
                type_hint=type_hint,
                required=name in required_fields,
                description=prop.get("description", ""),
                example=prop.get("example"),
                enum=prop.get("enum"),
            ))
        return fields

    def _resolve_ref(self, schema: dict) -> dict:
        ref = schema.get("$ref", "")
        if not ref:
            return schema
        # "#/components/schemas/Foo" or "#/definitions/Foo"
        parts = ref.lstrip("#/").split("/")
        cur = self._spec
        for p in parts:
            cur = cur.get(p, {})
        return cur
