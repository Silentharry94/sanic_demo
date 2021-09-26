#!/usr/bin/env python
# -*- coding: utf-8 -*-

# @Time    : 2021/9/23 4:47 下午
# @Author  : Hanley
# @File    : noobServe.py
# @Desc    :
import asyncio

import ujson
from pymongo import ReturnDocument
from sanic.views import HTTPMethodView

from config.constant import RedisKey
from core.base import BaseRequestHandler, ReturnResponse
from core.wrapper import uri_check


class Index(HTTPMethodView):

    @uri_check()
    async def get(self, request: BaseRequestHandler) -> ReturnResponse:
        tasks = [
            self.mysql_demo(request),
            self.mongo_demo(request),
            self.redis_demo(request),
        ]
        tasks_result = await asyncio.gather(*tasks)
        data = dict(zip([task.__name__ for task in tasks], tasks_result))
        return ReturnResponse(data=data)

    @uri_check()
    async def post(self, request: BaseRequestHandler) -> ReturnResponse:
        return ReturnResponse(data=dict(data="OK"))

    async def mysql_demo(self, request):
        # mysql demo
        table = request.parameter['table']
        span_id = request.parameter['span_id']
        sql = f"SELECT * FROM `{table}` WHERE `span_id` = '{span_id}'"
        mysql_result = await request.mysql.execute_sql(sql)
        mysql_result = [item for item in mysql_result]
        return mysql_result

    async def mongo_demo(self, request):
        # mongo demo
        mongo_result = await request.mongo.web_service.test.find_one_and_update(
            filter={"path": request.path, "method": request.method},
            update={"$set": {"path": request.path, "method": request.method, "parameter": request.parameter}},
            projection={"_id": 0},
            upsert=True,
            return_document=ReturnDocument.AFTER
        )
        return mongo_result

    async def redis_demo(self, request):
        # redis demo
        await request.redis.set(
            key="-".join([request.path, request.method]),
            value=ujson.dumps(request.parameter),
            expire=RedisKey.minute,
            exist="SET_IF_NOT_EXIST",
        )
        redis_result = await request.redis.get("-".join([request.path, request.method]))
        redis_result = ujson.loads(redis_result)
        return redis_result

    async def fetch_demo(self, request):
        # fetch demo
        fetch_result = await request.client.fetch_json(
            method="GET",
            url="https://api.bilibili.com/x/web-frontend/data/collector")
        return fetch_result
