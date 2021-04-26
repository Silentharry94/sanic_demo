#!/usr/bin/env python
# -*- coding: utf-8 -*-

# @Time    : 2021/4/23 6:49 下午
# @Author  : Hanley
# @File    : service.py
# @Desc    :

from library.common import singleton, Common, AsyncClientSession, create_async_session
from util.async_db import AsyncMySQLConnect, AsyncManager, AsyncMongodbConnect, AsyncRedis


@singleton
class Service:

    async def init_db(self):
        mongo_config = Common.yaml_config("mongo")
        redis_config = Common.yaml_config("redis")
        mysql_config = Common.yaml_config("mysql")
        _session = await create_async_session()
        mysql_database = AsyncMySQLConnect.init_db(mysql_config)

        self.client = AsyncClientSession(_session)
        self.redis = await AsyncRedis(redis_config).init_db()
        self.mongo = AsyncMongodbConnect(mongo_config).client
        self.mysql = AsyncManager(mysql_database)
