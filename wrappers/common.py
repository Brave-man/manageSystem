#! /usr/bin/env python
# -*- coding: utf-8 -*-
# __author__ = "David"
# Date: 2020-04-15

import functools

from tools.error import LoginError


# ------------------------------ wrappers ------------------------------


def with_auth_2_role(func):
    @functools.wraps(func)
    async def authCheck(self, *args, **kwargs):
        # --> 1.校验是否登录
        user_id = check_user_login(self)
        if not user_id:
            raise LoginError()

        # --> 4.校验通过, 执行业务操作
        await func(self, *args, **kwargs)

    return authCheck


# ------------------------------ functions -----------------------------

def check_user_login(hand_mod):
    """
    检查用户是否登录
    @param hand_mod: view层的handler
    @return:
    """
    user_id = hand_mod.check_login()
    return user_id
