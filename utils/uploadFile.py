#!/usr/bin/env python
# -*- coding: utf-8 -*-

# @Time    : 2021/9/23 2:25 下午
# @Author  : Hanley
# @File    : uploadFile.py
# @Desc    :
import copy

from obs import ObsClient


def upload_stream(filename, content, bucket_name='changst', **kwargs):
    """
    华为云文件上传
    """
    DEFAULT_CONFIG = dict(
        access_key_id='OZ0WAD9NZ9NLSZEOEL9L',
        secret_access_key='3UxoVl2AQlMTWhWpMoF60kPa4QjDfyKvuv8dXyn3',
        server='https://obs.cn-south-1.myhuaweicloud.com',
        ssl_verify=False,
        max_retry_count=1,
        timeout=20,
        chunk_size=65536,
        long_conn_mode=True
    )
    config = copy.copy(DEFAULT_CONFIG)
    for key in DEFAULT_CONFIG:
        if key in kwargs:
            config[key] = kwargs[key]
    obs_client = ObsClient(**config)
    resp = obs_client.putObject(bucket_name, filename, content)

    if resp.status > 300:
        return False, resp.errorMessage
    else:
        return True, ''
