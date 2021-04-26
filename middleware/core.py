#!/usr/bin/env python
# -*- coding: utf-8 -*-

# @Time    : 2021/4/25 12:55 下午
# @Author  : Hanley
# @File    : core.py
# @Desc    : 继承sanic类

from aioredis import Redis
from motor.motor_asyncio import AsyncIOMotorClient
from sanic import Sanic, Request
from sanic.compat import Header
from sanic.handlers import ErrorHandler
from sanic.models.protocol_types import TransportProtocol

from library.common import (
    AsyncClientSession
)
from library.initlog import logging
from util.async_db import AsyncManager


class BaseError(ErrorHandler):

    def default(self, request, exception):
        logging.warning(
            f"{request.path} raise web server error {exception}")
        return super().default(request, exception)


class BaseRequest(Request):

    def __init__(
            self,
            url_bytes: bytes,
            headers: Header,
            version: str,
            method: str,
            transport: TransportProtocol,
            app: Sanic,
            head: bytes = b"",
    ):
        super(BaseRequest, self).__init__(
            url_bytes,
            headers,
            version,
            method,
            transport,
            app,
            head
        )
        self.parameter = {}
        self._dict = {}

    @property
    def mysql(self) -> AsyncManager:
        return self.app.ctx.controller.mysql

    @property
    def mongo(self) -> AsyncIOMotorClient:
        return self.app.ctx.controller.mongo

    @property
    def redis(self) -> Redis:
        return self.app.ctx.controller.redis

    @property
    def aio_client(self) -> AsyncClientSession:
        return self.app.ctx.controller.client
