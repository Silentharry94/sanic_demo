#!/usr/bin/env python
# -*- coding: utf-8 -*-

# @Time    : 2019/12/19 下午4:21
# @Author  : Hanley
# @File    : wrapper.py
# @Desc    : 业务相关装饰器

import asyncio
import datetime
import decimal
import functools
import time
import traceback
from typing import Union

import ujson
from jsonschema import Draft4Validator, ValidationError
from playhouse.test_utils import count_queries
from sanic import response

from library.common import perf_time, Common
from library.constants import RETURN_MSG
from library.initlog import logging
from library.status_code import *
from middleware.core import BaseRequest
from model.test import UriConfig


def count_sql(func):
    async def wrapper(request: BaseRequest, *args, **kwargs):
        with count_queries() as counter:
            return_data = await func(request, *args, **kwargs)
        logging.debug(f"sql count: {counter.count}")
        return return_data

    return wrapper


class Response:
    __slots__ = (
        "code",
        "data",
        "msg",
        "kwargs",
        "decimal",
        "trace"
    )

    def __init__(self, code=CODE_1, *, data=None, msg=None,
                 decimal=False, trace=None, **kwargs):
        self.code = code
        self.data = data
        self.msg = msg
        self.kwargs = kwargs
        self.decimal = decimal
        self.trace = trace

    def for_dict(self, _dict: dict):
        for k in _dict:
            if isinstance(_dict[k], dict):
                self.format_float(_dict[k])
            else:
                if isinstance(_dict[k], (datetime.datetime, datetime.date)):
                    _dict[k] = Common.format_datetime(_dict[k])
                elif isinstance(_dict[k], (float, decimal.Decimal)):
                    _dict[k] = round(float(_dict[k]), 2)
                elif isinstance(_dict[k], list):
                    _dict[k] = type(_dict[k])([self.format_float(k) for k in _dict[k]])
                else:
                    continue
        return _dict

    def format_float(self, data: Union[dict, float, list]):
        if isinstance(data, dict):
            return self.for_dict(data)
        if isinstance(data, float):
            return round(float(data), 2)
        if isinstance(data, list):
            return list([self.format_float(k) for k in data])
        return data

    @property
    def body(self) -> dict:
        _response = {
            "code": self.code,
            "data": self.format_float(self.data) if self.decimal else self.data,
            "msg": RETURN_MSG.get(self.code, "unknown error")
        }
        if self.msg:
            _response["msg"] = self.msg
        if self.kwargs:
            _response.update(self.kwargs)
        return _response


def cost_time(func):
    def _cost(func_name, start_time):
        end_time = time.perf_counter()
        cost = (end_time - start_time) * 1000
        logging.debug(f">>>function: {func_name} duration: {cost}ms<<<")
        return

    if asyncio.iscoroutinefunction(func):
        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            start_time = time.perf_counter()
            return_data = await func(*args, **kwargs)
            _cost(func.__name__, start_time)
            return return_data
    else:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            start_time = time.perf_counter()
            return_data = func(*args, **kwargs)
            _cost(func.__name__, start_time)
            return return_data
    return wrapper


async def login_check(request: BaseRequest) -> bool:
    """do some check logic"""
    pass


def send_message(request: BaseRequest, response, trace):
    pass


async def access_limit(request: BaseRequest) -> bool:
    """do some check logic"""
    pass


async def permission_check(request: BaseRequest):
    """do some check logic"""
    pass


async def group_check(request, schema=None):
    mysql = request.mysql
    name = request.name
    _code = CODE_99
    _config = await mysql.get_or_none(UriConfig, name=name)
    if not _config:
        return CODE_101
    # 参数校验
    if schema or _config.schema:
        try:
            config_schema = ujson.loads(_config.schema)
            _schema = config_schema if config_schema else schema
            Draft4Validator(schema=_schema).validate(request.parameter)
        except ValidationError as e:
            logging.warning("{}: {}".format(CODE_102, e.message))
            _code = CODE_102

    return _code


def uri_check(return_format=response.json, schema=None):
    def validate(func):
        @functools.wraps(func)
        async def async_wrapper(request: BaseRequest, *args, **kwargs):
            logging.debug(f">>>request_id: {request._dict['request_id']} "
                          f"parameter: {request.parameter}")
            return_data = Response(CODE_99)
            try:
                return_data.code = await group_check(request, schema)
                if return_data.code == CODE_99:
                    return_data = await func(request, *args, **kwargs)
            except BaseException as e:
                logging.error(e)
                logging.error(traceback.format_exc())
                return_data.trace = e
                return_data.code = CODE_500
            start_time = request._dict.get("start_time")
            duration = (perf_time() - start_time) * 1000
            code = return_data.body.get('code', "unknown")
            logging.debug(f"path: {request.path} "
                          f"code: {code} duration: {duration}ms")
            return return_format(return_data.body)

        return async_wrapper

    return validate
