# --coding:utf-8--
from typing import Optional
from attrs import define, field
from core.api_object import BaseAPIObject
from core.router import router
from apis.demo.models import PostDataRequest, PostDataResponse


@define(kw_only=True)
@router.get("/get")
class GetAPI(BaseAPIObject):
    """httpbin GET 接口"""
    pass


@define(kw_only=True)
@router.post("/post")
class PostAPI(BaseAPIObject):
    """httpbin POST 接口"""
    request_body: Optional[PostDataRequest] = field(default=None)
    _response_model_cls = PostDataResponse
