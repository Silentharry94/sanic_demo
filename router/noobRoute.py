#!/usr/bin/env python
# -*- coding: utf-8 -*-

# @Time    : 2021/9/23 4:51 下午
# @Author  : Hanley
# @File    : noobServe.py
# @Desc    :

from sanic import Blueprint, HTTPResponse

from core.base import BaseRequestHandler
from views import noob

noob_bp = Blueprint(
    name="noob",
    url_prefix="/noob"
)


@noob_bp.middleware("request")
async def pre_request(request: BaseRequestHandler):
    """请求响应函数前"""
    # logging.debug(f"parameters: {request.parameter}")
    pass


@noob_bp.middleware("response")
async def post_response(request: BaseRequestHandler, response: HTTPResponse):
    """请求响应函数后"""
    pass


noob_bp.add_route(handler=noob.Index.as_view(), uri="/index")
