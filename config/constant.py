#!/usr/bin/env python
# -*- coding: utf-8 -*-

# @Time    : 2021/9/23 1:54 下午
# @Author  : Hanley
# @File    : constant.py
# @Desc    :
import os
import re


def make_file_path(config_name: str) -> str:
    curr_dir = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(curr_dir, config_name)


class RedisKey:
    second = 1
    minute = 60
    hour = minute * 60
    day = hour * 24
    month = day * 30


class Constant:
    # request headers content type
    octet_stream = re.compile('application/octet-stream')
    urlencoded_pattern = re.compile('application/x-www-form-urlencoded')
    json_pattern = re.compile('application/json')
    form_data = re.compile('multipart/form-data')
    xml = re.compile('application/xml')
    text = re.compile('text/plain')

    # config path
    YAML_CONFIG = make_file_path('config.yaml')
