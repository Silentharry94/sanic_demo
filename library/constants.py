#!/usr/bin/env python
# -*- coding: utf-8 -*-

# @Time    : 2021/4/17 12:00 上午
# @Author  : Hanley
# @File    : constants.py
# @Desc    :
import os
import re

from library.status_code import *

RETURN_MSG = {
    CODE_1: "Successfully return",
    CODE_0: "Error return",
    CODE_301: "Parameter Error",
    CODE_400: "Bad Request",
    CODE_404: "Url not Found",
    CODE_500: "Server error",

}


def make_file_path(config_name: str) -> str:
    curr_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(curr_dir, config_name)


class RedisKey:
    pass


class Constant:
    octet_stream = re.compile('application/octet-stream')
    urlencoded_pattern = re.compile('application/x-www-form-urlencoded')
    json_pattern = re.compile('application/json')
    form_data = re.compile('multipart/form-data')
    xml = re.compile('application/xml')
    text = re.compile('text/plain')

    INI_CONFIG = make_file_path("config.ini")
    YAML_CONFIG = make_file_path("config.yaml")

    NO_RECORD_URI = {}
