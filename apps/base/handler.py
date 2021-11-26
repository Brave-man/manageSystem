# -*- coding: utf-8 -*-
"""
-------------------------------------------------
    File Name:   handler
    Description: 
    Author:      wzj
    Date:        2019/12/13
-------------------------------------------------
    Change Activity:
-------------------------------------------------
"""

import time
import logging
import datetime
import tornado

from decimal import Decimal
from copy import copy
from urllib.parse import urlparse
from collections import Mapping
from abc import ABC
from typing import Optional, Any

from tornado.escape import json_encode, json_decode
from tornado.web import _ARG_DEFAULT as ARG_DEFAULT

from tools.usual import union2str, params_invalid_checker, buildingRequest, fetch_rpc
from tools.error import ArgError, BaseError
from config.globalConfig import SERVER_NAME, LOGIN_EXPIRE_DAY
from apps.core.token import check_token_is_valid, get_identity, get_user_uid, calculate_token


class BaseHandler(tornado.web.RequestHandler, ABC):
    """
    handler基类
    """

    need_login = False

    def __init__(self, application, request, **kwargs):
        super().__init__(application, request, **kwargs)
        self.content_body = {}
        self.content_type = ""

    def get_argument(self, name: str, default=ARG_DEFAULT, strip=True):
        args = getattr(self, 'log_args', {})
        v = super().get_argument(name, default, strip)
        args[name] = v
        setattr(self, 'log_args', args)
        return v

    #  -------基础工具包-----------

    def prepare(self):
        self.content_type = self.request.headers.get('Content-Type', '')
        try:
            if 'json' in self.content_type and self.request.body:
                logging.error(self.request.body)
                self.content_body = json_decode(self.request.body)
            else:
                self.content_body = {}
        except Exception:
            raise ArgError(msg='校验失败')

        if self.need_login and not self.check_login():
            raise BaseError(code=-1, msg='请登录后操作')

    def get_json_argument(self, argument_name, default=None, show_argument_name=None):
        argu = self.content_body.get(argument_name, default)
        if argu is None:
            raise ArgError(msg='参数{0}异常'.format(show_argument_name or argument_name))
        else:
            return argu

    def get_int_argument(self, argument_name, default=None, show_argument_name=None) -> int:
        """
        获取整形参数

        :param argument_name: 参数名
        :param default: 默认值，为None时表示改字段必填
        :param show_argument_name: 错误提示时该参数名
        :return: int or raise error
        """
        argu = self.get_argument(argument_name, '') or self.content_body.get(argument_name, default)
        if argu is None:
            raise ArgError(msg='参数{0}异常'.format(show_argument_name or argument_name))
        else:
            try:
                arg = int(argu)
            except ValueError:
                msg = '请确认参数{argument_name}为整数'.format(argument_name=show_argument_name or argument_name)
                raise ArgError(msg=msg)
            else:
                return arg

    def get_str_argument(self, argument_name, default=None, show_argument_name=None, msg=None) -> str:
        """
        获取str参数

        :param msg: 消息
        :param argument_name: 参数名
        :param default: 默认值，为None时表示改字段必填
        :param show_argument_name: 错误提示时该参数名
        :return: int or raise error
        """
        argu = self.get_argument(argument_name, '') or self.content_body.get(argument_name, default)
        if argu is None:
            msg = msg or '参数{0}异常'.format(show_argument_name or argument_name)
            raise ArgError(msg=msg)
        return self._xss(argu)

    def get_body_argument(self,
                          name: str,
                          default: Optional[Any] = ARG_DEFAULT,
                          argument_type: Optional[Any] = None,
                          allow_values: Optional[list] = None,
                          show_name: Optional[str] = None) -> Optional[Any]:
        """
        获取body参数
        :param name: 名称
        :param default: 默认值
        :param argument_type: 参数类型
        :param allow_values: 允许值
        :param show_name: 展示名称
        :return:
        """
        value = self.content_body.get(name, default)
        if value == ARG_DEFAULT:
            msg = "参数{argument_name}为必填参数".format(argument_name=show_name or name)
            raise ArgError(msg=msg)

        if value is not None:
            if argument_type is not None:
                if not isinstance(value, argument_type):
                    msg = "参数{argument_name}类型非法".format(argument_name=show_name or name)
                    raise ArgError(msg=msg)

        if allow_values is not None:
            if value not in allow_values:
                msg = "参数{argument_name}值非法".format(argument_name=show_name or name)
                raise ArgError(msg=msg)

        return value

    def write_error(self, status_code, **kwargs):
        # 接管程序内所有的异常, 避免前端获取到 500 error
        self.set_header('Content-Type', 'application/json')
        if "exc_info" in kwargs:
            _, e, tb = kwargs['exc_info']
            self.set_status(200)
            setattr(self, 'status_code', status_code)
            self.simplewrite(code=getattr(e, 'code', 0), msg=getattr(e, 'msg', '服务异常'), status_code=status_code)
        else:
            self.finish(json_encode({'msg': '服务异常201', 'code': 0}))

    def simplewrite(self, code=1, msg='success', data=None, **kwargs):
        date_fmt = kwargs.pop('date_fmt', '%Y-%m-%d')
        time_fmt = kwargs.pop('time_fmt', '%Y-%m-%d %M:%H:%S')
        res = {
            'code': code,
            'msg': msg,
            'time': int(time.time()),
            'request_id': self.get_str_argument('request_id', ''),
            'data': data if data is not None else {}
        }
        res.update(kwargs)
        self.write(self._formate_datatime(res, time_fmt=time_fmt, date_fmt=date_fmt))

    def write(self, chunk):
        if isinstance(chunk, Mapping):
            code = chunk.get('code', 0)
            msg = chunk.get('msg', '服务异常')
        else:
            code = getattr(chunk, 'code', 0)
            msg = getattr(chunk, 'msg', '服务异常')
        setattr(self, 'return_code', code)
        setattr(self, 'return_msg', msg)
        super().write(chunk)

    @staticmethod
    def _datetime_to_string(dt, formate="%m-%d %H:%M"):
        return dt.strftime(formate)

    def _formate_datatime(self, rd, time_fmt="%m-%d %H:%M", date_fmt='%Y-%m-%d'):
        data = copy(rd)
        if isinstance(rd, datetime.datetime):
            return self._datetime_to_string(rd, time_fmt)
        if isinstance(rd, datetime.date):
            return self._datetime_to_string(rd, date_fmt)
        if isinstance(rd, Decimal):
            return int(rd)
        if rd is None:
            return ''
        if isinstance(rd, dict):
            for key, value in rd.copy().items():
                if isinstance(value, Decimal):
                    data[key] = int(value)
                if isinstance(value, Mapping):
                    data[key] = self._formate_datatime(value, time_fmt, date_fmt)
                if isinstance(value, datetime.datetime):
                    data[key] = self._datetime_to_string(value, time_fmt)
                if isinstance(value, datetime.date):
                    data[key] = self._datetime_to_string(value, date_fmt)
                if isinstance(value, list):
                    data[key] = [self._formate_datatime(item, time_fmt, date_fmt) for item in value]
                if value is None:
                    data[key] = ''
        if isinstance(rd, list):
            data = [self._formate_datatime(item, time_fmt, date_fmt) for item in rd]
        return data

    @staticmethod
    async def fetch_rpc(req, language=""):
        """
        fetch url
        with json decode
        :param req: HTTPRequest object
        :param language: local-language
        :return: result
        """

        response = await fetch_rpc(req, language)
        return response

    @staticmethod
    def buildingRequest(url, method="GET", headers=None, req_body=None, acc_rpc_time_out=10, validate_cert=False):
        """
        :param url: url address
        :param method: GET/POST/..
        :param headers: { "KEY": VALUE}
        :param req_body: {"key1": value1, "keys": value2}
        :param acc_rpc_time_out: default 10 sec
        :param validate_cert: need cert check
        :return: req object
        """
        headers = {} if headers is None else headers
        req_body = {} if req_body is None else req_body
        return buildingRequest(url, method=method, headers=headers,
                               req_body=req_body,
                               acc_rpc_time_out=acc_rpc_time_out,
                               validate_cert=validate_cert)

    # -----------------------------basic func----------------------------------
    # 获取用户选择的系统语言版本
    def get_language(self):
        """
        从header中获取 language
        """
        language = self.request.headers.get('Sys-Language')
        if not language:
            language = 'zh'
        return language

    # Allows us to get the previous URL
    def get_referring_url(self):
        referer = '/'
        try:
            _, _, referer, _, _, _ = urlparse(self.request.headers.get('Referer'))
        except AttributeError:
            pass
        return referer

    @staticmethod
    def _xss(data):
        """
        xss checker
        """
        if data:
            return data.replace(" ", "")
        else:
            return ""

    @staticmethod
    def params_invalid_checker(allowed_keys, params):
        """
        非法参数名校验
        :param allowed_keys:
        :param params:
        :return:
        """
        return params_invalid_checker(allowed_keys, params)

    @staticmethod
    def any2str(data):
        return union2str(data)

    def set_cors_header(self):
        # 设置跨域请求头，只有在需要跨域的接口处使用
        self.set_header('Access-Control-Allow-Origin', '*')
        self.set_header('Access-Control-Allow-Headers', 'x-requested-with')
        self.set_header('Access-Control-Allow-Methods', 'POST, GET, PUT, DELETE, OPTIONS')
        self.set_header('Access-Control-Allow-Credentials', 'true')

    def check_login(self):
        """
        检查是否登录
        :return:
        """
        cookie_name = "%s_TOKEN" % SERVER_NAME
        token = self.get_secure_cookie(cookie_name)

        return check_token_is_valid(token)

    @property
    def identity(self):
        """
        公司ID
        :return:
        """
        cookie_name = "%s_TOKEN" % SERVER_NAME
        token = self.get_secure_cookie(cookie_name)
        identity = get_identity(token)
        if not identity:
            raise BaseError(code=0, msg="非法请求")

        return identity

    @property
    def user_uid(self):
        """
        用户ID
        :return:
        """
        cookie_name = "%s_TOKEN" % SERVER_NAME
        token = self.get_secure_cookie(cookie_name)
        user_uid = get_user_uid(token)
        if not user_uid:
            raise BaseError(code=0, msg="非法请求")

        return user_uid

    def set_login(self, identity, user_uid, login_expire_day=LOGIN_EXPIRE_DAY):
        """
        设置登录
        :param identity: 身份 teacher 老师 student 学生
        :param user_uid: 用户uid
        :param login_expire_day: 登录失效日期
        :return:
        """
        token = calculate_token(identity, user_uid, login_expire_day)
        cookie_name = "%s_TOKEN" % SERVER_NAME
        self.set_secure_cookie(cookie_name, token, LOGIN_EXPIRE_DAY)
