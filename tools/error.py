# -*- coding: utf-8 -*-
"""
-------------------------------------------------
    File Name:   error
    Description: 
    Author:      wzj
    Date:        2019-09-26
-------------------------------------------------
    Change Activity:
-------------------------------------------------
"""

class BaseError(Exception):
    code = 0
    msg = '服务异常'

    def __init__(self, msg=None, code=None):
        self.code = code or self.code
        self.msg = msg or self.msg

class SMSError(BaseError):
    pass

class DoesNotExistsError(BaseError):
    code = 0
    msg = '记录不存在'


class ArgError(BaseError):
    code = 0
    msg = '参数异常'


class LoginError(BaseError):
    """
    登录异常
    """
    code = -1
    msg = "未登录"


class PermissionError(BaseError):
    """
    权限异常
    """
    code = -2
    msg = "无权访问"


class PayCallBackError(Exception):
    """
    支付回调异常捕获
    """
    pass


class RequestOriginError(BaseError):
    """
    请求来源非法
    """
    code = -4
    msg = "Illegal Request"
