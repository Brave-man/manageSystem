#! /usr/bin/env python
# -*- coding: utf-8 -*-
# __author__ = "David"
# Date  : 2021-11-25
# Digest:

from tornado.web import url

from apps.classes.classHandler import ClassHandler

urls = [
    url(r"/teacher/class", ClassHandler),  # 老师班级列表查询
]
