#! /usr/bin/env python
# -*- coding: utf-8 -*-

import time

from tools.usual import calculate_md5
from config.globalConfig import LOGIN_EXPIRE_DAY, MD5_KEY


def calculate_token(identity, user_uid, login_expire_day=LOGIN_EXPIRE_DAY):
    """
    计算token
    :param identity: 身份
    :param user_uid: 用户uid
    :param login_expire_day: 过期时间
    :return:
    """
    set_time = int(time.time()) + login_expire_day * 24 * 60 * 60
    to_str = f"{identity}:{user_uid}:{set_time}:{MD5_KEY}"

    token = "{identity}:{user_uid}:{set_time}:{md5}".format(
        identity=identity,
        user_uid=user_uid,
        set_time=set_time,
        md5=calculate_md5(to_str)
    )

    return token


def check_token_is_valid(token: bytes):
    """
    检查token是否有效
    :param token: token
    :return:
    """
    valid = False
    if not token:
        return valid

    # noinspection PyBroadException
    try:
        identity, user_uid, set_time, md5 = token.decode().split(":")
        if all([identity, user_uid, set_time, md5]):
            if int(time.time()) < int(set_time):
                valid = True
    except BaseException:
        pass

    return valid


def get_user_uid(token: bytes):
    """
    获取当前用户userid
    :param token:
    :return:
    """
    user_uid = None
    if token:
        # noinspection PyBroadException
        try:
            identity, user_uid, set_time, md5 = token.decode().split(":")
        except BaseException:
            pass

    return user_uid


def get_identity(token: bytes):
    """
    获取登录身份
    :param token:
    :return:
    """
    identity = None
    if token:
        # noinspection PyBroadException
        try:
            identity, user_uid, set_time, md5 = token.decode().split(":")
        except BaseException:
            pass

    return identity
