#!/usr/bin/env python
# -*- coding: utf-8 -*-

# @Time    : 2021/4/22 2:03 下午
# @Author  : Hanley
# @File    : app.py
# @Desc    :


from peewee import *

from library.common import Common
from util.async_db import AsyncMySQLConnect

mysql_config = Common.yaml_config("mysql")
_mysql = AsyncMySQLConnect.init_db(mysql_config)


class BaseModel(Model):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    class Meta:
        database = _mysql
