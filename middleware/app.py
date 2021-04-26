#!/usr/bin/env python
# -*- coding: utf-8 -*-

# @Time    : 2021/4/18 3:06 下午
# @Author  : Hanley
# @File    : app.py
# @Desc    : app中间件|请求中间件（无业务相关可在此添加）

import inspect
import re

from sanic import Sanic, Request, HTTPResponse

from controller.service import Service
from library.common import (
    Common,
    Constant, perf_time, str_now
)
from library.initlog import logging
from middleware.core import BaseError, BaseRequest
from script.init_tables import PreTable
from url.urls import blue_group

app = Sanic(
    "james",
    error_handler=BaseError(),
    request_class=BaseRequest
)
app.blueprint(blue_group())


def parse_parameter(request: Request) -> dict:
    """
    根据content_type，解析请求参数
    :param request:
    :return:
    """
    content_type = request.content_type
    parameter = {}
    for key, values in request.args.items():
        parameter.setdefault(key, values[0])
    if re.match(Constant.form_data, content_type):
        if request.form:
            for key, values in request.form.items():
                parameter.setdefault(key, values[0])
    if re.match(Constant.urlencoded_pattern, content_type):
        if request.form:
            for key, values in request.form.items():
                parameter.setdefault(key, values[0])
    if re.match(Constant.xml, content_type):
        if request.body:
            parameter.update(Common.xml2dict(request.body.decode()))
    if re.match(Constant.text, content_type):
        if request.body:
            parameter.update(text=request.body.decode())
    if re.match(Constant.json_pattern, content_type):
        if request.json:
            parameter.update(request.json)
    return parameter


@app.listener('before_server_start')
async def before_server_start(app: Sanic, loop):
    """
    创建数据库连接(mysql, mongo, redis)
    创建aiohttp session
    :param app:
    :param loop:
    :return:
    """
    controller = Service()
    await controller.init_db()
    setattr(app.ctx, "controller", controller)
    logging.debug(f"{inspect.stack()[0].function} done")


@app.listener('after_server_start')
async def after_server_start(app: Sanic, loop):
    """
    生成uri_config数据
    :param app:
    :param loop:
    :return:
    """
    lock_key = "pre_sync_config_table_lock"
    r_lock = await app.ctx.controller.redis.setnx(lock_key, str_now())
    if r_lock:
        PreTable(app.name, app.router.routes.values())
        await app.ctx.controller.redis.expire(lock_key, 10)
    logging.debug(f"{inspect.stack()[0].function} done")


@app.listener('before_server_stop')
async def before_server_stop(app: Sanic, loop):
    """
    关闭数据库连接(mysql, redis)
    关闭aiohttp session
    :param app:
    :param loop:
    :return:
    """
    app.ctx.controller.redis.close()
    await app.ctx.controller.redis.wait_closed()
    await app.ctx.controller.client.close()
    await app.ctx.controller.mysql.close()
    logging.debug(f"{inspect.stack()[0].function} done")


@app.listener('after_server_stop')
async def after_server_stop(app, loop):
    logging.debug(f"{inspect.stack()[0].function} done")


@app.on_request
async def pre_uri_check(request: BaseRequest):
    """
    解析参数
    :param request:
    :return:
    """
    inner_dict = {
        "start_time": perf_time(),
        "request_id": str(request.id),
    }
    parameter = parse_parameter(request)
    request.parameter = parameter
    request._dict = inner_dict
    logging.debug(f"{inspect.stack()[0].function} done")


@app.on_response
async def post_uri_check(request: BaseRequest, response: HTTPResponse):
    logging.debug(f"{inspect.stack()[0].function} done")
