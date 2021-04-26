#!/usr/bin/env python
# -*- coding: utf-8 -*-

# @Time    : 2021/4/22 2:03 下午
# @Author  : Hanley
# @File    : init_tables.py
# @Desc    :

import os
import sys
import traceback
from collections import Iterable

proPath = os.path.dirname(
    os.path.dirname(
        os.path.abspath(__file__)))  # noqa
sys.path.append(proPath)  # noqa
from library.initlog import logging
from library.common import datetime_now, singleton
from model.base import _mysql
from model.test import *


def generate_subclass(sub_model: list, list_model: list) -> list:
    for item in sub_model:
        if item.__subclasses__():
            generate_subclass(item.__subclasses__(), list_model)
        if item.__name__ not in list_model and len(item.__subclasses__()) == 0:
            list_model.append(item)
    return list_model


def find_orm() -> list:
    sub_model = BaseModel.__subclasses__()
    list_model = generate_subclass(sub_model, [])
    list_model = [item for item in list_model if not item.table_exists()]
    return list_model


def insert_single_data(model, dataList, chunk_size=100):
    with _mysql.atomic():
        try:
            logging.debug(f"start insert data to {model}")
            for i in range(0, len(dataList), chunk_size):
                logging.debug(f"data: {dataList[i: i + chunk_size]}")
                model.insert_many(dataList[i: i + chunk_size]).execute()
        except BaseException:
            logging.error(traceback.format_exc())


def insert_multi_data(modelList, dataDict):
    for model in modelList:
        if model.select().count() > 0:
            logging.debug(f"{model.__name__} already had data, so continue")
            continue
        for key, value in dataDict.items():
            if model.__name__ == key:
                insert_single_data(model, value)


def complete_table():
    """
    补全mysql表
    :return:
    """
    miss_model = find_orm()
    with _mysql.allow_sync():
        with _mysql.atomic():
            logging.debug(f"Missing models: "
                          f"{[model.__name__ for model in miss_model]}")
            if len(miss_model):
                logging.debug("start create tables...")
                _mysql.create_tables(miss_model)
                logging.debug("end create tables")
    logging.debug("complete_table done")


@singleton
class PreTable:
    __name = None

    def __init__(self, name, routers):
        if not self.__name:
            self.sync_uri_config(routers)
            self.__name = name
        else:
            self.__name = name

    def sync_uri_config(self, routers: Iterable):
        """
        项目启动自动更新接口配置表
        创建新路由接口|启用之前禁用接口|禁用之前启用接口
        :param routers:
        :return:
        """
        logging.debug(f"start sync_uri_config")
        now = datetime_now()
        with _mysql.allow_sync():
            with _mysql.atomic():
                _last = UriConfig.select().order_by(-UriConfig.code).first()
                code = _last.code + 1 if _last else 10 << 10
                query_existing_uri = UriConfig.select().dicts()
                existing_uri = {uri["path"]: uri for uri in query_existing_uri}
                running_uri = set()
                for route in routers:
                    path = route.path if route.path.startswith("/") else "/" + route.path
                    running_uri.add(path)
                    _uri = existing_uri.get(path)
                    if not _uri:
                        _uri_dict = {
                            "code": code,
                            "path": path,
                            "name": route.name,
                            "regex": 1 if route.regex else 0,
                            "pattern": route.pattern if route.pattern else "",
                            "method": ",".join(route.methods),
                        }
                        logging.debug(f"_uri_dict: {_uri_dict}")
                        UriConfig.insert(_uri_dict).execute()
                        code += 1
                    else:
                        update_dict = {
                            "status": 1,
                            "update_time": now,
                            "name": route.name,
                            "regex": 1 if route.regex else 0,
                            "pattern": route.pattern,
                            "method": ",".join(route.methods),
                        }
                        UriConfig.update(update_dict).where(
                            UriConfig.path == path).execute()
                effect_existing_uri = {uri for uri in existing_uri if existing_uri[uri]["status"] == 1}
                disabled_uri = list(effect_existing_uri - running_uri)
                if disabled_uri:
                    UriConfig.update({"status": 0, "update_time": now}).where(
                        UriConfig.path << disabled_uri).execute()
            logging.debug("sync uri config done")


if __name__ == '__main__':
    complete_table()
