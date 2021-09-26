#!/usr/bin/env python
# -*- coding: utf-8 -*-

# @Time    : 2021/9/22 7:41 下午
# @Author  : Hanley
# @File    : dbClient.py
# @Desc    :

import copy
import time
import traceback
from typing import Union
from urllib.parse import quote_plus

import aioredis
import pymongo
import redis
from aioredis import Redis
from motor.motor_asyncio import AsyncIOMotorClient
from peewee import PeeweeException, DoesNotExist, RawQuery
from peewee_async import PooledMySQLDatabase, Manager
from pymysql.err import Error

from libs.log import logging


class AsyncMongodb:
    """
    motor多连接
    peer_conn = host + port + user
    """
    __slots__ = (
        "config",
        "peer_conn",
        "client"
    )
    __conn = {}

    def __init__(self, config: dict):
        self.config = dict(config)
        self.init_db()

    def init_db(self):
        config_client = {}
        self.peer_conn = "_".join([
            self.config["HOST"], str(self.config["PORT"])])
        if self.config["USER"]:
            self.peer_conn = "_".join([self.peer_conn, self.config["USER"]])
        if not self.__conn.get(self.peer_conn):
            url = self._connect_url()
            self.client = AsyncIOMotorClient(
                url, maxPoolSize=100, maxIdleTimeMS=300000,
                waitQueueMultiple=10, serverSelectionTimeoutMS=5000)
            config_client.setdefault("config", self.config)
            config_client.setdefault("client", self.client)
            self.__conn.setdefault(self.peer_conn, config_client)
            logging.debug(f"connect mongodb {self.peer_conn} successful")
        else:
            self.client = self.__conn[self.peer_conn]["client"]
            self.config = self.__conn[self.peer_conn]["config"]

    def _connect_url(self):
        url = "mongodb://"
        domain = "{host}:{port}/".format(
            host=self.config["HOST"], port=self.config["PORT"]
        )

        if self.config["USER"] and self.config["PASSWORD"] and self.config["AUTH_DB"]:
            authentication = "{username}:{password}@".format(
                username=quote_plus(self.config["USER"]),
                password=quote_plus(self.config["PASSWORD"])
            )
            domain = "{host}:{port}/".format(
                host=self.config["HOST"],
                port=self.config["PORT"]
            )
            param = "?authSource={auth_db}".format(
                auth_db=self.config["AUTH_DB"]
            )
            url = "".join([url, authentication, domain, param])
        else:
            url = "".join([url, domain])
        return url


class AsyncPeewee(PooledMySQLDatabase):
    """
    异步MySQL连接
    peer_conn: host + port + database
    """
    __conn = {}

    @staticmethod
    def init_db(config: dict) -> PooledMySQLDatabase:
        _config = dict(config)
        peer_conn = "_".join([
            _config["HOST"], str(_config["PORT"]), _config["DATABASE"]])
        if not AsyncPeewee.__conn.get(peer_conn):
            _database = AsyncPeewee(
                database=_config["DATABASE"],
                max_connections=_config['MAX_CONNECTIONS'],
                host=_config['HOST'],
                user=_config['USER'],
                password=_config["PASSWORD"],
                port=_config['PORT']
            )
            AsyncPeewee.__conn[peer_conn] = _database
            logging.debug(f"connect mysql {peer_conn} successful")
        return AsyncPeewee.__conn[peer_conn]

    def execute_sql(self, sql, params=None, commit=True):
        try:
            return super(AsyncPeewee, self).execute_sql(sql, params, commit)
        except Exception as exc:
            if not isinstance(exc, (PeeweeException, Error)):
                raise exc
            logging.warning("will retry connect mysql")
            if not self.is_closed():
                self.close()
                self.connect()

            return super(AsyncPeewee, self).execute_sql(sql, params, commit)


class AsyncPeeweeManager(Manager):
    """
    peewee_async高级API
    """

    async def get_or_none(self, source_, *args, **kwargs):
        try:
            return await self.get(source_, *args, **kwargs)
        except DoesNotExist:
            return

    async def execute_sql(self, sql: str, params: Union[None, tuple, list] = None):
        """
        使用：
            sql = 'select * from user where name = %s and gender = %s'
            params = ['好帅的人', 'm']

            res = await AsyncManager().execute_sql(sql, params)
            for r in res:
                print(r['id'])
        :param sql:
        :param params:
        :return:
        """
        query = RawQuery(sql, params, _database=self.database)

        # for r in await self.execute(query):
        #     yield RawQueryResult(r)
        return await self.execute(query)


class AsyncRedis:
    """
    异步Redis连接
    peer_conn: address + db
    """
    __slots__ = (
        "config",
        "client",
    )
    __conn = {}

    def __init__(self, config: dict):
        self.config = dict(config)

    async def init_db(self) -> Redis:
        peer_conn = "_".join([
            self.config["ADDRESS"], str(self.config["DB"])])
        if self.__conn.get(peer_conn):
            self.client = self.__conn[peer_conn]
        else:
            default_config = dict(address='', db=None, password=None, ssl=None,
                                  encoding=None, commands_factory=Redis,
                                  minsize=1, maxsize=10, parser=None,
                                  timeout=None, pool_cls=None,
                                  connection_cls=None, loop=None)
            connect_config = copy.copy(default_config)
            for key in connect_config:
                if key.upper() in self.config:
                    connect_config[key] = self.config.pop(key.upper())
            self.client = await aioredis.create_redis_pool(**connect_config)
            self.__conn[peer_conn] = self.client
            logging.debug(f"connect redis {peer_conn} successful")
        return self.__conn[peer_conn]


class SyncMongodb:
    __slots__ = (
        "config",
        "client",
    )
    __conn = {}

    def __init__(self, config: dict):
        self.config = dict(config)
        self.init_db()

    def init_db(self):
        host = self.config["HOST"]
        port = self.config["PORT"]
        user = self.config["USER"]
        password = self.config["PASSWORD"]
        auth_db = self.config["AUTH_DB"]

        peer_conn = "_".join([host, str(port)])
        if user:
            peer_conn += "_" + user
        if self.__conn.get(peer_conn):
            self.client = self.__conn[peer_conn]
            return self.client

        url = "mongodb://"
        domain = "{host}:{port}/".format(
            host=host, port=port
        )
        if user and password and auth_db:
            authentication = "{username}:{password}@".format(
                username=quote_plus(user),
                password=quote_plus(password)
            )
            domain = "{host}:{port}/".format(
                host=host,
                port=port
            )
            param = "?authSource={auth_db}".format(
                auth_db=auth_db
            )
            url = "".join([url, authentication, domain, param])
        else:
            url = "".join([url, domain])

        self.client = pymongo.MongoClient(url, serverSelectionTimeoutMS=5000)
        logging.debug(f"mongodb connect successful")


class SyncPeewee(PooledMySQLDatabase):
    __conn = {}

    @staticmethod
    def init_db(config: dict) -> PooledMySQLDatabase:
        peer_db = "_".join([
            config["HOST"], str(config["PORT"]), config["DATABASE"]])
        if not SyncPeewee.__conn.get(peer_db):
            SyncPeewee.__conn[peer_db] = SyncPeewee(
                database=config["DATABASE"],
                max_connections=config['MAX_CONNECTIONS'],
                stale_timeout=config['TIMEOUT'],
                timeout=config['TIMEOUT'],
                host=config['HOST'],
                user=config['USER'],
                password=config["PASSWORD"],
                port=config['PORT']
            )
        return SyncPeewee.__conn[peer_db]

    def execute_sql(self, sql, params=None, commit=True):
        try:
            return super(SyncPeewee, self).execute_sql(sql, params, commit)
        except Exception as exc:
            if not isinstance(exc, (PeeweeException, Error)):
                raise exc
            logging.warning("will retry connect mysql")
            if not self.is_closed():
                self.close()
                self.connect()

            return super(SyncPeewee, self).execute_sql(sql, params, commit)


class SyncRedis:
    __slots__ = (
        "config",
        "client"
    )
    __conn = {}

    def __init__(self, config: dict):
        self.config = dict(config)
        self.init_db()

    def init_db(self):
        peer_db = "_".join([
            self.config["HOST"], str(self.config["PORT"]), str(self.config["DB"])])
        if self.__conn.get(peer_db):
            self.client = self.__conn[peer_db]
            return self.client
        retry = 3
        self.client, i = None, 0
        default_config = dict(
            host='',
            port='',
            db='',
            decode_responses=True)
        connect_config = copy.copy(default_config)
        for key in connect_config:
            if key in self.config:
                connect_config[key] = self.config.pop(key)
        while i < retry:
            try:
                pool = redis.ConnectionPool(**connect_config)
                self.client = redis.Redis(connection_pool=pool)
                if self.client:
                    logging.debug(f"redis connect successful")
                    break
                else:
                    logging.warning("第[%d]连接失败，继续" % i)
            except BaseException:
                logging.error(traceback.format_exc())
                time.sleep(1)
            i += 1
        self.__conn[peer_db] = self.client
        return self.client
