#! /usr/bin/env python
# -*- coding: utf-8 -*-
# __author__ = "David"
# Date  : 2021-11-21
# Digest: 登录

from abc import ABC

from apps.base.handler import BaseHandler
from apps.user.userService import UserService
from tools.error import ArgError


class LoginHandler(BaseHandler, ABC):
    """
    登录Handler
    """
    need_login = False

    async def post(self):
        """
        用户登录
        :return:
        """
        identity = self.get_body_argument("identity")  # 身份: teacher:老师 student:学生
        username = self.get_body_argument("username")  # 用户名
        password = self.get_body_argument("password")  # 密码

        if identity not in ["student", "teacher"]:
            ArgError(msg="identity参数非法")

        # 登录认证
        user_obj = UserService()
        user_uid = user_obj.auth_user_login(identity, username, password)

        self.set_login(identity, user_uid)
        self.simplewrite()


class LogoutHandler(BaseHandler, ABC):
    """
    退出登录Handler
    """
    need_login = False

    async def get(self):
        """
        退出登录
        :return:
        """
        self.clear_all_cookies()
        self.simplewrite()


class UserProfileHandler(BaseHandler, ABC):
    """
    查询个人信息
    """

    need_login = True

    async def get(self):
        """
        查询个人信息
        :return:
        """
        identity = self.identity
        user_uid = self.user_uid

        # 查询个人信息
        user_obj = UserService()
        data = user_obj.query_user_profile(identity, user_uid)
        data["identity"] = identity
        self.simplewrite(data=data)
