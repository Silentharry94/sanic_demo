#!/usr/bin/env python
# -*- coding: utf-8 -*-

# @Time    : 2021/4/15 10:13 上午
# @Author  : Hanley
# @File    : app.py
# @Desc    :

import argparse
import os

from library.common import Common
from library.initlog import logging
from middleware.app import app
from script.init_tables import complete_table

parser = argparse.ArgumentParser()
parser.add_argument(
    '-e', '--env', default="dev",
    choices=["dev", "prod", "staging"],
    type=str, help='start project environment')
parser.add_argument(
    '-p', '--port', default=8080,
    type=int, help='start project port')
parser.add_argument(
    '-c', '--cert', type=str,
    help='start project ssl cert file path')
parser.add_argument(
    '-k', '--key', type=str,
    help='start project ssl key file path')
args = parser.parse_args()


def main():
    Common.init_config_file(args.env)
    complete_table()
    _config = Common.yaml_config()
    app.config.update(_config)
    logging.debug(f"start {args.env} server at {args.port}")
    ssl = None
    if args.cert and args.key:
        ssl = {
            'cert': args.cert,
            'key': args.key
        }
    app.run(host="0.0.0.0", port=args.port, backlog=2048, ssl=ssl,
            workers=os.cpu_count(), debug=False, access_log=False)


if __name__ == '__main__':
    main()
