#! /usr/bin/env python
# -*- coding: utf-8 -*-
# __author__ = "David"
# Date  : 2021-11-24
# Digest:

from tornado.web import url

from apps.user.userHandler import LoginHandler, UserProfileHandler, LogoutHandler

urls = [
    url(r"/user/login", LoginHandler),  # 登录
    url(r"/user/logout", LogoutHandler),  # 退出登录
    url(r"/user/profile", UserProfileHandler)  # 查询个人信息
]
