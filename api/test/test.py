#!/usr/bin/env python
# -*- coding: utf-8 -*-

# @Time    : 2021/4/16 2:32 下午
# @Author  : Hanley
# @File    : test_url.py
# @Desc    : test_group

import os

from sanic import Blueprint

from controller.service import Service
from library.common import Common
from library.initlog import logging
from middleware.core import BaseRequest
from middleware.wrapper import Response
from middleware.wrapper import uri_check
from model.test import AsyncDB
from util.async_db import AsyncMongodbConnect

test_bp = Blueprint("test_group", url_prefix="/test")


@test_bp.route('/fetch', methods={"GET", "POST"})
@uri_check()
async def fetch(request: BaseRequest):
    """
    ping handler
    :param request:
    :return:
    """
    
    url = "https://api.bilibili.com/x/web-frontend/data/collector"
    res = await request.aio_client.fetch_json("GET", url)
    return Response(data=res)


@test_bp.route('/ping', methods={"GET", "POST"})
@uri_check()
async def ping(request: BaseRequest):
    """
    ping handler
    :param request:
    :return:
    """
    config = request.app.config
    result = [config for _ in range(20)]
    return Response(data=result, **config)


@test_bp.route(r'/pattern/<redirect:([\w\W]*)>', methods={"GET", "POST"})
@uri_check()
async def t_pattern(request: BaseRequest, redirect: str, *args):
    """
    :param request:
    :param redirect:
    :param args:
    :return:
    """
    logging.debug(f"redirect: {redirect}")
    logging.debug(f"args: {args}")
    logging.debug(f"req: {request}")
    config = request.app.config
    result = [config for _ in range(20)]
    return Response(data=result)


@test_bp.route('/args', methods={"GET", "POST"})
@uri_check()
async def raise_error(request: BaseRequest):
    """

    :param request:
    :return:
    """
    logging.debug(f"{request.parameter}")
    data = 1 / 0
    return Response(data=data)


@test_bp.route('/db', methods={"GET", "POST"})
@uri_check()
async def own_db(request: BaseRequest):
    """
    :param request:
    :return:
    """
    _service = Service()

    mongo_config = Common.yaml_config("mongo")
    mysql_sql = AsyncDB.insert(
        pid=os.getpid(),
        type="MYSQL",
        type_id=id(request.mysql),
        request_id=request._dict['request_id']
    )
    mongo_sql = AsyncDB.insert(
        pid=os.getpid(),
        type="MONGODB",
        type_id=id(request.mongo),
        request_id=request._dict['request_id']
    )
    redis_sql = AsyncDB.insert(
        pid=os.getpid(),
        type="REDIS",
        type_id=id(request.redis),
        request_id=request._dict['request_id']
    )
    client_sql = AsyncDB.insert(
        pid=os.getpid(),
        type="CLIENT",
        type_id=id(request.aio_client),
        request_id=request._dict['request_id']
    )
    controller_sql = AsyncDB.insert(
        pid=os.getpid(),
        type="CONTROLLER",
        type_id=id(AsyncMongodbConnect(mongo_config).client),
        request_id=request._dict['request_id']
    )
    service_sql = AsyncDB.insert(
        pid=os.getpid(),
        type="SERVICE",
        type_id=id(_service),
        request_id=request._dict['request_id']
    )

    await request.mysql.execute(mysql_sql)
    await request.mysql.execute(mongo_sql)
    await request.mysql.execute(redis_sql)
    await request.mysql.execute(client_sql)
    await request.mysql.execute(controller_sql)
    await request.mysql.execute(service_sql)
    return Response()
