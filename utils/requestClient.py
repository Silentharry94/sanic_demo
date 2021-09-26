#!/usr/bin/env python
# -*- coding: utf-8 -*-

# @Time    : 2021/9/23 1:50 下午
# @Author  : Hanley
# @File    : requestClient.py
# @Desc    :
import uuid

import ujson
from aiohttp import TCPConnector, ClientSession
from requests import Session, adapters

from libs.bolts import catch_exc
from libs.log import logging


class AioClient:
    """
    async aiohttp client
    """
    __slots__ = (
        "session",
        "log"
    )

    def __new__(cls, *args, **kwargs):
        if not hasattr(cls, '_instance'):
            cls._instance = super(AioClient, cls).__new__(cls)
        return cls._instance

    async def init_session(self, log=logging) -> ClientSession:
        self.log = log
        tcp_connector = TCPConnector(
            keepalive_timeout=15,
            limit=600,
            limit_per_host=300,
        )
        self.session = ClientSession(connector=tcp_connector)
        return self.session

    async def request(self, method, url, **kwargs):
        kw_str = ujson.dumps(kwargs)
        if len(kw_str) > 100:
            kw_str = kw_str[:100]
        self.log.debug(f"{method} {url} {kw_str}")
        return await self.session.request(method, url, **kwargs)

    @catch_exc(calc_time=True, default_data={})
    async def fetch_json(self, method, url, **kwargs):
        kw_str = ujson.dumps(kwargs)
        if len(kw_str) > 100:
            kw_str = kw_str[:100]
        async with self.session.request(method, url, **kwargs) as response:
            result = await response.json()
            self.log.debug(f"{method} {url} {kw_str}")
            return result

    async def close(self):
        await self.session.close()


class RequestsClient(Session):

    def __new__(cls, *args, **kwargs):
        if not hasattr(cls, '_instance'):
            cls._instance = super(RequestsClient, cls).__new__(cls)
        return cls._instance

    def __init__(self, time_out=30, pool_num=10, pool_max_size=50, max_retries=3):
        super(RequestsClient, self).__init__()
        self._time_out = time_out
        self._pool_num = pool_num
        self._pool_max_size = pool_max_size
        self._max_retries = max_retries
        self.mount("http://", adapters.HTTPAdapter(
            pool_connections=self._pool_num,
            pool_maxsize=self._pool_max_size,
            max_retries=self._max_retries
        ))
        self.mount("https://", adapters.HTTPAdapter(
            pool_connections=self._pool_num,
            pool_maxsize=self._pool_max_size,
            max_retries=self._max_retries
        ))

    @catch_exc(calc_time=True)
    def request(self, method, url, headers=None, timeout=None, **kwargs):
        timeout = timeout or self._time_out
        headers = headers or {}
        if not headers.get("X-Request-ID"):
            headers["X-Request-ID"] = uuid.uuid4().hex
        return super().request(
            method, url, headers=headers, timeout=timeout, **kwargs)
