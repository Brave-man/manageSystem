# -*- coding: utf-8 -*-
"""
-------------------------------------------------
    File Name:   http
    Description: 
    Author:      wzj
    Date:        2019-09-26
-------------------------------------------------
    Change Activity:
-------------------------------------------------
"""

import logging
import traceback
from tornado.httpclient import HTTPRequest, AsyncHTTPClient, HTTPError
from tornado.httputil import url_concat, urlencode
from tornado.escape import json_decode, json_encode

from .error import BaseError


class GetHTTPRequest(HTTPRequest):
    """
    praam: 查询参数 字典对象
    """
    def __init__(self, url, param=None, **kwargs):
        if param:
            url = url_concat(url, param)
        super().__init__(url, "GET", **kwargs)


class PostHTTPRequest(HTTPRequest):
    """
    仅支持简单的application/x-www-form-urlencoded类型的post请求
    data: None or dict
    """
    def __init__(self, url, data=None, param=None, **kwargs):
        body = data or {}
        body.update(kwargs.pop('body', {}))
        if param:
            url = url_concat(url, param)
        super().__init__(url, 'POST', body=urlencode(body), **kwargs)


class PostJsonHTTPRequest(HTTPRequest):
    """
    仅支持简单的application/json类型的post请求
    """
    def __init__(self, url, data=None, param=None, **kwargs):
        body = data or {}
        body.update(kwargs.pop('body', {}))
        headers = {"content-type": "application/json"}
        if param:
            url = url_concat(url, param)
        kwargs['headers'] = headers
        super().__init__(url, 'POST', body=json_encode(body), **kwargs)


class HTTPContent(object):
    """远程http请求

    如果发生异常，get/post会直接raise
    """

    @classmethod
    async def get(cls, url: str, param=None, **kwargs):
        param = {} if param is None else param
        request = GetHTTPRequest(url, param, **kwargs)
        return await cls.send_request(request)

    @classmethod
    async def post(cls, url, data=None, param=None, **kwargs):
        data = {} if data is None else data
        request = PostHTTPRequest(url, data=data, param=param, **kwargs)
        return await cls.send_request(request)

    @classmethod
    async def post_json(cls, url, data=None, param=None, **kwargs):
        data = {} if data is None else data
        request = PostJsonHTTPRequest(url, data=data, param=param, **kwargs)
        return await cls.send_request(request)

    @classmethod
    async def send_request(self, request):
        try:
            response = await AsyncHTTPClient().fetch(request)
            rjson = json_decode(response.body)
        except (HTTPError, ValueError) as e:
            msg = '发起请求异常'
            logging.error(traceback.format_exc())
            logging.error(request.url)
            logging.error('header:{header}, body:{body}'.format(header=request.headers, body=request.body))
            raise BaseError(msg=msg)
        else:
            return rjson

    @classmethod
    def encode_multipart_formdata(self, fields, files):
        # 封装multipart/form-data post请求
        boundary = b'WebKitFormBoundaryh4QYhLJ34d60s2tD'
        boundary_u = boundary.decode('utf-8')
        crlf = b'\r\n'
        l = []
        for (key, value) in fields:
            l.append(b'--' + boundary)
            temp = 'Content-Disposition: form-data; name="%s"' % key
            l.append(temp.encode('utf-8'))
            l.append(b'')
            if isinstance(value, str):
                l.append(value.encode())
            else:
                l.append(value)
        key, filename, value = files
        l.append(b'--' + boundary)
        temp = 'Content-Disposition: form-data; name="%s"; filename="%s"' % (key, filename)
        l.append(temp.encode('utf-8'))
        temp = 'Content-Type: img/%s' % filename.split('.')[1]
        l.append(temp.encode('utf-8'))
        l.append(b'')
        l.append(value)
        l.append(b'--' + boundary + b'--')
        l.append(b'')
        body = crlf.join(l)
        content_type = 'multipart/form-data; boundary=%s' % boundary_u
        return content_type, body

