#! /usr/bin/env python
# -*- coding: utf-8 -*-
# __author__ = "David"
# Date  : 2021-11-25
# Digest:

from tornado.web import url

from apps.course.courseHandler import CourseHandler

urls = [
    url(r"/teacher/courser", CourseHandler),  # 老师课程管理
]
