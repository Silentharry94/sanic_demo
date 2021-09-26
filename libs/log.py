#!/usr/bin/env python
# -*- coding: utf-8 -*-

# @Time    : 2021/9/23 1:52 下午
# @Author  : Hanley
# @File    : log.py
# @Desc    :
import os

from loguru import logger

BASE_PATH = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
DEFAULT_LOG_PATH = os.path.join(BASE_PATH, "log")
DEFAULT_FORMAT = "{time:YYYY-MM-DD HH:mm:ss} | {level} | {process.id} | {name} | {function} | {line} | {message}"

API_LOG_PATH = os.path.join(DEFAULT_LOG_PATH, "api")
API_HANDLERS = [
    {
        "sink": "%s/{time:YYYYMMDD}.log" % API_LOG_PATH,
        "enqueue": True,
        "backtrace": False,
        "rotation": "00:00",
        "retention": "30 days",
        "format": DEFAULT_FORMAT,
        "filter": lambda x: x["extra"].get("channel", '') == "api"
    }
]


class ServerLog:
    __conn = {}

    def __init__(self, channel: str, handlers: list):
        if not self.__conn.get(channel):
            self.channel = channel
            _ = [logger.add(**h) for h in handlers]
            client = logger.bind(channel=channel)
            self.__conn.setdefault(channel, client)
        self.client = self.__conn[channel]


logging = ServerLog("api", API_HANDLERS).client
