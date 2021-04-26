#!/usr/bin/env python
# -*- coding: utf-8 -*-

# @Time    : 2021/4/16 2:34 下午
# @Author  : Hanley
# @File    : urls.py
# @Desc    :

from sanic import Blueprint
from sanic.blueprint_group import BlueprintGroup

from api.test.test import test_bp


def blue_group() -> BlueprintGroup:
    blueprints = []
    blueprints.append(test_bp)
    api = Blueprint.group(*blueprints, url_prefix="/api", version="v1")
    return api
