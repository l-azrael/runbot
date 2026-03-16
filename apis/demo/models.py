# --coding:utf-8--
from typing import Optional
from attrs import define, field


@define
class PostDataRequest:
    """httpbin /post 接口请求体"""
    name: str = field(
        default=None,
        metadata={"description": "用户名", "example": "test_user"},
    )
    age: int = field(
        default=None,
        metadata={"description": "年龄", "example": 25},
    )


@define
class PostDataResponse:
    """httpbin /post 接口响应"""
    json: Optional[dict] = field(default=None)
    url: Optional[str] = field(default=None)
    headers: Optional[dict] = field(default=None)
