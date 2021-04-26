#!/usr/bin/env python
# -*- coding: utf-8 -*-

# @Time    : 2021/4/19 3:27 下午
# @Author  : Hanley
# @File    : test.py
# @Desc    :

import datetime

from peewee import *

from model.base import BaseModel


class AreaItem(BaseModel):
    code = CharField(max_length=255, primary_key=True, verbose_name="编码")
    name = CharField(max_length=255, verbose_name="名称")
    city_code = CharField(max_length=255, index=True, verbose_name="市区编码")
    province_code = CharField(max_length=255, verbose_name="省份编码")

    class Meta:
        table_name = "area"
        verbose_name = "区/县表"


class UriConfig(BaseModel):
    code = IntegerField(unique=True, verbose_name="接口编码")
    path = CharField(max_length=128, default="", unique=True, verbose_name="接口地址")
    name = CharField(max_length=63, default="", unique=True, verbose_name="接口名称")
    regex = SmallIntegerField(default=0, verbose_name="是否使用正则")
    pattern = CharField(max_length=256, default="", verbose_name="正则表达式")
    description = CharField(max_length=256, default="", verbose_name="接口描述")
    method = CharField(default="GET", max_length=64, verbose_name="请求方式")
    login_check = SmallIntegerField(default=1, verbose_name="登录权限")
    access_check = SmallIntegerField(default=1, verbose_name="访问权限")
    schema = TextField(default="", verbose_name="参数校验")
    status = SmallIntegerField(index=True, default=1, verbose_name="启用标记")
    create_time = DateTimeField(default=datetime.datetime.now, verbose_name="创建时间")
    update_time = DateTimeField(default=datetime.datetime.now, verbose_name="更新时间")

    class Meta:
        table_name = "uri_config"


class AsyncDB(BaseModel):
    request_id = CharField(max_length=64, default="", verbose_name="请求id")
    pid = CharField(max_length=16, default="", verbose_name="pid")
    type = CharField(max_length=32, default="", verbose_name="数据类型")
    type_id = CharField(max_length=32, default="", verbose_name="类型id")

    class Meta:
        table_name = "async_db"
