# --coding:utf-8--
import json
from typing import Generic, TypeVar, Optional, Type
from json.decoder import JSONDecodeError

import requests
from requests import sessions
from genson import SchemaBuilder

from core.router import ROUTE_META_ATTR
from core.storage.cache import cache
from core.storage.config import config
from core.storage.schema import schema
from core.exceptions import HttpRequestError
from core.log.log import logger

T = TypeVar("T")


class Response(Generic[T]):
    def __init__(self, raw: requests.Response, model_cls: Optional[Type[T]] = None):
        self.raw = raw
        self.status_code = raw.status_code
        self.elapsed = raw.elapsed.total_seconds()
        self._body = None
        self._model: Optional[T] = None

        try:
            self._body = raw.json()
        except (JSONDecodeError, ValueError):
            self._body = raw.text

        if model_cls and isinstance(self._body, dict):
            try:
                self._model = model_cls(**self._body)
            except Exception:
                pass

    @property
    def body(self):
        return self._body

    @property
    def response_model(self) -> Optional[T]:
        return self._model

    def __repr__(self):
        return f"<Response [{self.status_code}]>"


class BaseAPIObject(Generic[T]):
    """所有接口对象的基类，子类通过 @router.xxx 装饰器声明路由"""

    IS_HTTP_RETRY = False
    HTTP_RETRY_COUNTS = 3
    HTTP_RETRY_INTERVAL = 2

    # 子类可覆盖，指定响应模型类
    _response_model_cls: Optional[Type[T]] = None

    def _get_route(self) -> dict:
        route = getattr(self.__class__, ROUTE_META_ATTR, None)
        if not route:
            raise AttributeError(f"{self.__class__.__name__} 未使用 @router 装饰器声明路由")
        return route

    def _build_request(self) -> dict:
        """将接口对象属性转换为 requests 参数字典，子类可覆盖"""
        route = self._get_route()
        host = config.get("host") or ""
        headers = cache.get("headers") or {"Content-Type": "application/json"}
        token = cache.get("token")
        if token:
            headers["token"] = token

        req = {
            "method": route["method"],
            "url": host + route["path"],
            "headers": headers,
            "_api_name": self.__class__.__name__,
            "_http_retry": self.IS_HTTP_RETRY,
            "_retry_counts": self.HTTP_RETRY_COUNTS,
            "_retry_interval": self.HTTP_RETRY_INTERVAL,
        }

        # 自动提取 attrs 字段到请求参数
        if hasattr(self, "__attrs_attrs__"):
            for attr in self.__attrs_attrs__:
                val = getattr(self, attr.name, None)
                if val is None or attr.name.startswith("_"):
                    continue
                if attr.name == "request_body":
                    import attr as _attr
                    if _attr.has(type(val)):
                        req["json"] = _attr.asdict(val)
                    else:
                        req["json"] = val
                elif attr.name == "query_params":
                    req["params"] = val if isinstance(val, dict) else _attr.asdict(val)
                elif attr.name == "path_params" and isinstance(val, dict):
                    req["url"] = req["url"].format(**val)

        return req

    def _do_send(self, req: dict) -> requests.Response:
        method = req.pop("method")
        url = req.pop("url")
        # 清理内部控制字段
        internal_keys = [k for k in req if k.startswith("_")]
        for k in internal_keys:
            req.pop(k)

        with sessions.Session() as session:
            return session.request(method=method, url=url, **req)

    def send(self) -> Response[T]:
        # 导入中间件（触发注册）
        import core.middlewares.logging_mw  # noqa
        import core.middlewares.retry_mw    # noqa
        from core.middlewares.base import MiddlewareChain

        req = self._build_request()

        def _send(r: dict) -> dict:
            raw = self._do_send(dict(r))
            if raw.status_code >= 400:
                raise HttpRequestError(raw.status_code)
            try:
                body = raw.json()
            except (JSONDecodeError, ValueError):
                body = raw.text

            # 自动生成并存储 schema
            if isinstance(body, dict) and body.get("code") != 500:
                builder = SchemaBuilder()
                builder.add_object(body)
                schema.set(self.__class__.__name__, builder.to_schema())

            return {
                "status_code": raw.status_code,
                "elapsed": raw.elapsed.total_seconds(),
                "body": body,
                "_raw": raw,
            }

        chain = MiddlewareChain(_send)
        result = chain.execute(req)
        raw_resp = result.get("_raw")
        return Response(raw_resp, self._response_model_cls)
