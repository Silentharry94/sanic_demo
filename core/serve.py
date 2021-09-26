#!/usr/bin/env python
# -*- coding: utf-8 -*-

# @Time    : 2021/9/23 3:09 下午
# @Author  : Hanley
# @File    : serve.py
# @Desc    :
from sanic import Sanic, json, HTTPResponse

from core.base import BaseErrorHandler, ServeContext, ReturnResponse, ServeConfig
from core.base import BaseRequestHandler
from libs.log import logging

noob_serve = Sanic(
    "NOOB-SERVE",
    error_handler=BaseErrorHandler(),
    request_class=BaseRequestHandler,
    config=ServeConfig(),
)


@noob_serve.listener('main_process_start')
async def main_process_start(app: Sanic, listener):
    """主进程启动前"""
    logging.info(f'start {app.name} successfully')
    pass


@noob_serve.listener('main_process_stop')
async def main_process_stop(app: Sanic, listener):
    """主进程停止后"""
    pass


@noob_serve.listener('before_server_start')
async def before_server_start(app: Sanic, loop):
    """子进程启动前"""
    serve_context = ServeContext(config=app.config, loop=loop)
    await serve_context.init_connection()
    app.ctx = serve_context
    pass


@noob_serve.listener('after_server_start')
async def after_server_start(app: Sanic, loop):
    """子进程启动后"""
    pass


@noob_serve.listener('before_server_stop')
async def before_server_stop(app: Sanic, loop):
    """子进程停止前"""
    await app.ctx.close_connection()
    pass


@noob_serve.listener('after_server_stop')
async def after_server_stop(app, loop):
    """子进程停止后"""
    pass


@noob_serve.on_request
async def pre_request(request: BaseRequestHandler):
    """请求响应函数前"""
    # logging.debug(f"parameter: {request.parameter}")
    pass


@noob_serve.on_response
async def post_request(request: BaseRequestHandler, response: ReturnResponse) -> HTTPResponse:
    """请求响应函数后"""
    # logging.debug(f"{request.method} {request.path} {response.body}")
    return json(response.dict_body)
