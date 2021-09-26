#!/usr/bin/env python
# -*- coding: utf-8 -*-

# @Time    : 2021/9/23 1:50 下午
# @Author  : Hanley
# @File    : bolts.py
# @Desc    :
import asyncio
import datetime
import fcntl
import filecmp
import re
import time
import traceback
from decimal import Decimal
from functools import wraps

import xmltodict
import yaml

from config.constant import Constant
from libs.log import logging


def str_now(format="%Y-%m-%d %X"):
    return time.strftime(format)


def datetime_now():
    return datetime.datetime.now()


def perf_time():
    return time.perf_counter()


def yaml_config(key=None, file_path=Constant.YAML_CONFIG):
    with open(file_path, 'r') as f:
        config = yaml.safe_load(f)
    if key:
        return config.get(key)
    return config


def format_datetime(data):
    if isinstance(data, datetime.datetime):
        return data.strftime("%Y-%m-%d %H:%M:%S")
    elif isinstance(data, datetime.date):
        return data.strftime("%Y-%m-%d")
    else:
        return data


def validate_url(url: str):
    if not str:
        return
    pattern = re.compile(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+')
    result = re.findall(pattern, url)
    return result


def validate_phone(phone_number: str):
    _mobile_pattern = r"1[356789]\d{9}"
    _landline_pattern = r"\d{3}-\d{8}|\d{4}-\d{7}"
    mobile_pattern = re.compile(_mobile_pattern)
    landline_pattern = re.compile(_landline_pattern)
    _check = lambda p: p.findall(phone_number)
    if len(phone_number) == 11 and "-" not in phone_number:
        result = _check(mobile_pattern)
    else:
        result = _check(landline_pattern)
    return result


def validate_email(email: str):
    pattern = re.compile(r"[a-zA-Z0-9_-]+@[a-zA-Z0-9_-]+(?:\.[a-zA-Z0-9_-]+)")
    result = re.findall(pattern, email)
    if result:
        return result
    else:
        return result


def validate_id_card(id_card: str):
    pattern = re.compile(
        r"[1-9]\d{5}(?:18|19|(?:[23]\d))\d{2}(?:(?:0[1-9])|(?:10|11|12))(?:(?:[0-2][1-9])|10|20|30|31)\d{3}[0-9Xx]")
    result = re.findall(pattern, id_card)
    if result:
        return result
    else:
        return result


def is_number(s: str):
    if s.count('.') == 1:  # 小数
        new_s = s.split('.')
        left_num = new_s[0]
        right_num = new_s[1]
        if right_num.isdigit():
            if left_num.isdigit():
                return True
            elif left_num.count('-') == 1 and left_num.startswith('-'):  # 负小数
                tmp_num = left_num.split('-')[-1]
                if tmp_num.isdigit():
                    return True
    elif s.count(".") == 0:  # 整数
        if s.isdigit():
            return False
        elif s.count('-') == 1 and s.startswith('-'):  # 负整数
            ss = s.split('-')[-1]
            if ss.isdigit():
                return False
    return False


def decimal_dict(_dict: dict):
    for k in _dict:
        if isinstance(_dict[k], dict):
            format_decimal(_dict[k])
        else:
            if isinstance(_dict[k], float):
                _dict[k] = float(round(Decimal(_dict[k]), 2))
            elif isinstance(_dict[k], str):
                if is_number(_dict[k]):
                    _dict[k] = float(round(Decimal(float(_dict[k])), 2))
            elif isinstance(_dict[k], list):
                _dict[k] = list([format_decimal(k) for k in _dict[k]])
            else:
                continue
    return _dict


def format_decimal(data):
    if isinstance(data, dict):
        return decimal_dict(data)
    if isinstance(data, float):
        return float(round(Decimal(data), 2))
    if isinstance(data, str):
        if is_number(data):
            return float(round(Decimal(float(data)), 2))
        else:
            return data
    if isinstance(data, list):
        return list(([format_decimal(k) for k in data]))
    return data


def cp_file(source_file, target_file):
    if filecmp.cmp(target_file, source_file):
        return
    with open(source_file, 'r') as sf:
        with open(target_file, 'w') as tf:
            fcntl.lockf(tf.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
            while True:
                data = sf.read(4069)
                if not data:
                    break
                tf.write(data)


def encode_multipart_formdata(fields, files):
    # 封装multipart/form-data post请求
    boundary = b'WebKitFormBoundaryh4QYhLJ34d60s2tD'
    boundary_u = boundary.decode('utf-8')
    crlf = b'\r\n'
    l = []
    for (key, value) in fields:
        l.append(b'--' + boundary)
        temp = 'Content-Disposition: form-data; name="%s"' % key
        l.append(temp.encode('utf-8'))
        l.append(b'')
        if isinstance(value, str):
            l.append(value.encode())
        else:
            l.append(value)
    key, filename, value = files
    l.append(b'--' + boundary)
    temp = 'Content-Disposition: form-data; name="%s"; filename="%s"' % (key, filename)
    l.append(temp.encode('utf-8'))
    temp = 'Content-Type: img/%s' % filename.split('.')[1]
    l.append(temp.encode('utf-8'))
    l.append(b'')
    l.append(value)
    l.append(b'--' + boundary + b'--')
    l.append(b'')
    body = crlf.join(l)
    content_type = 'multipart/form-data; boundary=%s' % boundary_u
    return content_type, body


def dict2xml(dict_data, root="xml") -> str:
    """
    字典转xml
    dict_data: 字典数据
    root：根结点标签
    """
    _dictXml = {root: dict_data}
    xmlstr = xmltodict.unparse(_dictXml, pretty=True)
    return xmlstr


def xml2dict(xml_data) -> dict:
    """
    xml转dict
    xml_data: xml字符串
    return: dict字符串
    """
    data = xmltodict.parse(xml_data, process_namespaces=True)
    return dict(list(data.values())[0])


def cost_time(func_name, start_time, log=logging):
    end_time = perf_time()
    cost = (end_time - start_time) * 1000
    log.debug(f">>>function: {func_name} duration: {cost}ms<<<")
    return cost


def catch_exc(calc_time: bool = False, log=logging, default_data=None):
    def valid(func):
        @wraps(func)
        async def async_wrapper(*args, **kwargs):
            start_time = perf_time()
            return_data = default_data
            try:
                return_data = await func(*args, **kwargs)
            except Exception as e:
                log.error(e)
                log.error(traceback.format_exc())
            if calc_time:
                cost_time(func.__name__, start_time, log=log)
            return return_data

        @wraps(func)
        def sync_wrapper(*args, **kwargs):
            start_time = perf_time()
            return_data = {}
            try:
                return_data = func(*args, **kwargs)
            except Exception as e:
                log.error(e)
                log.error(traceback.format_exc())
            if calc_time:
                cost_time(func.__name__, start_time, log=log)
            return return_data

        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        else:
            return sync_wrapper

    return valid
