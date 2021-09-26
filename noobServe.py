#!/usr/bin/env python
# -*- coding: utf-8 -*-

# @Time    : 2021/9/23 3:04 下午
# @Author  : Hanley
# @File    : noobServe.py
# @Desc    :

# import argparse
# import multiprocessing

from sanic import Blueprint

from core.serve import noob_serve
from router.noobRoute import noob_bp

# parse = argparse.ArgumentParser()
# parse.add_argument("--host", default="0.0.0.0", type=str, help="服务启动绑定IP")
# parse.add_argument("--port", default=8003, type=int, help="服务启动绑定端口")
# parse.add_argument("--workers", default=multiprocessing.cpu_count(), type=int, help="服务自动进程数")
# args = parse.parse_args()

noob_route = Blueprint.group(noob_bp, url_prefix="/api", version=1)
noob_serve.blueprint(noob_route)

# if __name__ == '__main__':
#     noob_serve.run(host=args.host, port=args.port, workers=args.workers)
