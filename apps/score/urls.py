#! /usr/bin/env python
# -*- coding: utf-8 -*-
# __author__ = "David"
# Date  : 2021-11-25
# Digest:

from tornado.web import url

from apps.score.scoreHandler import StudentScoreHandler, TeacherScoreHandler

urls = [
    url(r"/student/course/score", StudentScoreHandler),  # 学生成绩查询
    url(r"/teacher/course/score", TeacherScoreHandler),  # 老师对学生的成绩管理
]
