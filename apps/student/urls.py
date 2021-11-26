#! /usr/bin/env python
# -*- coding: utf-8 -*-
# __author__ = "David"
# Date  : 2021-11-26
# Digest:

from tornado.web import url

from apps.student.studentHandler import StudentHandler

urls = [
    url(r"/teacher/student", StudentHandler),  # 老师对学生的管理
]
