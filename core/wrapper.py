#!/usr/bin/env python
# -*- coding: utf-8 -*-

# @Time    : 2021/9/24 4:49 下午
# @Author  : Hanley
# @File    : wrapper.py
# @Desc    :
import asyncio
import traceback
from functools import wraps

from config.return_code import CODE_0
from core.base import ReturnResponse, BaseRequestHandler
from libs.log import logging


def send_message(request: BaseRequestHandler, response):
    pass


async def group_check(request: BaseRequestHandler, schema, login_check):
    return CODE_0


def uri_check(schema=None, login_check: bool = False):
    def validate(func):
        @wraps(func)
        async def async_wrapper(self, request: BaseRequestHandler, *args, **kwargs) -> ReturnResponse:
            try:
                check_code = await group_check(request, schema, login_check)
                if check_code == CODE_0:
                    if not asyncio.iscoroutinefunction(func):
                        return_data = func(self, request, *args, **kwargs)
                    else:
                        return_data = await func(self, request, *args, **kwargs)
                else:
                    return_data = ReturnResponse(check_code)
            except Exception as e:
                logging.error(e)
                logging.error(traceback.format_exc())
                return_data = ReturnResponse(CODE_0, trace=traceback.format_exc())
            send_message(request, return_data.dict_body)

            if request.app.config.get("ENV", "") == "prod":
                return_data.trace = None
            return return_data

        return async_wrapper

    return validate
