# -*- coding: utf-8 -*-
# @Time    : 2019/08/20 下午1:54
# @Author  : Sean
# @Site    : beacon_business
# @Software: PyCharm

import os
import json
import zipfile
import logging
import time
import bcrypt
import hashlib
import datetime

from urllib.parse import urlencode
from tornado.escape import json_encode, json_decode, recursive_unicode
from tornado.httpclient import HTTPRequest
from tornado.httpclient import AsyncHTTPClient
from config.globalConfig import static_url_prefix


def calculate_md5(key: str):
    m = hashlib.md5()
    m.update(bytes(key.encode()))
    return m.hexdigest().lower()


getMd5 = calculate_md5


def generate_uid():
    return calculate_md5(str(time.time()))


def calculate_sha1(key: str):
    sha = hashlib.sha1()
    sha.update(bytes(key.encode()))
    return sha.hexdigest()


def calculate_password(password: str):
    return bcrypt.hashpw(bytes(password.encode()), bcrypt.gensalt(8)).decode()


def auth_password(password: str, encrypt_pwd: str):
    return bytes(encrypt_pwd.encode()) == bcrypt.hashpw(password.encode(), encrypt_pwd.encode())


def fmt_datetime(dt: datetime.datetime, fmt='%Y-%m-%d'):
    return dt.strftime(fmt)


def union2str(data):
    """
    将任何类型转为python字符串
    :param data:  可以是单个 bytes 字符串，也可以是 list, dict, set, tuple
    :return:
    """
    return recursive_unicode(data)


def json_encode_dump(data):
    """
    将混合的json对象压制成utf8 json packge
    :param data:
    :return:
    """
    return json_encode(data)


def json_decode_loads(data):
    """
    解析json package , unioncode 转换
    :param data:
    :return:
    """
    return json_decode(data)


def make_file_url(relative_path):
    """
    生成文件访问的URL
    :param relative_path: 文件相对路径
    :return: file_url 文件访问的URL
    """
    file_url = os.path.join(static_url_prefix, relative_path)
    return file_url


def params_invalid_checker(allowed_keys, params):
    """
    检查非法参数
    :param allowed_keys:
    :param params:
    :return:
    """
    invalid_keys = set(params) - set(allowed_keys)
    if invalid_keys:
        invalid_keys = list(invalid_keys)
    else:
        invalid_keys = None
    return invalid_keys


def make_folder(file_path):
    """
    生成文件夹，若文件夹存在，则不需要生成
    :param file_path: 文件路径
    :return: None
    """
    if not os.path.exists(file_path):
        os.makedirs(file_path)


def write_file(file_path, file):
    """
    文件的写入
    :param file_path: 文件路径
    :param file: 文件内容
    :return: None
    """
    with open(file_path, 'wb') as f:
        f.write(file)
        logging.info('success:文件写入成功！')


def make_path(file_info):
    """
    以file_info中parent_path作为第一级目录，以当前年月日组成的目录为第二级目录
    :param file_info: {'parent_path': '父级目录', 'file_name': '文件名'}
    :return: path 文件存放的绝对路径
    """
    parent_path = file_info.get('parent_path')
    file_name = file_info.get('file_name')

    # 创建一级目录
    make_folder(parent_path)

    # 创建二级目录
    folder_create_time = time.strftime('%Y%m%d')
    second_parent_path = os.path.join(parent_path, folder_create_time)
    make_folder(second_parent_path)

    path = os.path.join(second_parent_path, file_name)
    return path


def delete_file(file_path):
    """
    删除文件
    :param file_path:
    :return:
    """
    if os.path.exists(file_path):
        os.remove(file_path)
    return True


def delete_all(folder_path):
    """
    删除该目录下的所有文件
    :param filepath:
    :return:
    """
    if os.path.exists(folder_path):
        for i in os.listdir(folder_path):
            path_file = os.path.join(folder_path, i)
            if os.path.isfile(path_file):
                os.remove(path_file)
            else:
                delete_all(path_file)
                os.rmdir(path_file)


def calculate_time_str(now_timestamp, interval, format='%Y%m%d%H%M%S'):
    """
    计算当前时间间隔多少秒后的字符串时间
    :param now_timestamp: 当前时间戳
    :param interval: 间隔秒数
    :return: 按照格式，格式化后的时间字符串 (now_str, expire_str)
    """
    now_struct = time.localtime(now_timestamp)
    now_str = time.strftime(format, time.struct_time(now_struct))

    expire_timestamp = now_timestamp + interval
    expire_struct = time.localtime(expire_timestamp)
    expire_str = time.strftime(format, time.struct_time(expire_struct))
    return now_str, expire_str


def compress_zipfile(filepath_list, target_folder, filename):
    """
    压缩zipfile
    :param filepath_list: 待压缩的文件路径列表
    :param target_folder: 目标压缩文件夹
    :param filename: 文件名
    """
    if not os.path.exists(target_folder):
        os.mkdir(target_folder)

    target_path = os.path.join(target_folder, filename)

    with zipfile.ZipFile(target_path, mode='w') as zf:
        for filepath, arcname in filepath_list:
            zf.write(filepath, arcname, zipfile.ZIP_DEFLATED)
    return target_path


def access_verify(params, sign, stime):
    """
    内部系统 接口你签名
    :param params: 参数，dict, 必须有
    :param sign: 加密参数
    :param stime: 14位 时间戳 str(int(time.time()*10000))
    :return:
    """
    sign_base = ""
    for key in sorted(params.keys(), reverse=True):
        value = params[key]
        if value not in [None, "", [], {}]:
            sign_base += ",{}={}".format(key.upper(), str(value).upper())

    sign_str = getMd5(stime + getMd5(sign_base) + sign)
    return sign_str


def buildingRequest(url, method="GET", headers=None, req_body=None, acc_rpc_time_out=10, validate_cert=False):
    """
    :param url: url address
    :param method: GET/POST/..
    :param headers: { "KEY": VALUE}
    :param req_body: {"key1": value1, "keys": value2}
    :param acc_rpc_time_out: default 10 sec
    :param validate_cert:
    :return: req object
    """
    headers = {} if headers is None else headers
    req_body = {} if req_body is None else req_body

    if method == "GET":
        req = HTTPRequest(url, method="GET",
                          request_timeout=acc_rpc_time_out,
                          headers=headers, validate_cert=validate_cert)
    elif method == "POST":
        if type(req_body) == dict:
            body = urlencode(req_body)
        else:
            body = req_body
        req = HTTPRequest(url, method=method,
                          body=body,
                          request_timeout=acc_rpc_time_out,
                          headers=headers, validate_cert=validate_cert)
    else:
        req = HTTPRequest(url, method=method, request_timeout=acc_rpc_time_out)
    return req


async def fetch_rpc(req, language=""):
    """
    fetch url
    with json decode
    :param req: HTTPRequest object
    :param language: local-language
    :return: result
    """
    rpc_data = {}
    success = True
    try:
        # 统一为rpc 增加语言类型参数
        if isinstance(req.headers, dict):
            req.headers["Sys-Language"] = language
        else:
            req.headers.add("Sys-Language", language)
        response = await AsyncHTTPClient().fetch(req)
        rpc_data = json.loads(str(response.body, encoding="utf-8"))
    except Exception as ex:
        success = False
        except_args = ex.args
        except_type = type(ex).__name__
        template = "An exception of type {0} occurred. Arguments:\n{1!r}"
        message = template.format(except_type, except_args)
        logging.debug("-----------%s" % message)
        if "Timeout" in except_args[1]:
            exception_type = "timeout"
            exception_intro = "==从rpc获取数据超时"
        else:
            exception_type = "error"
            exception_intro = "==从rpc获取数据出错"
        rpc_data = {"exception_type": exception_type, "exception_intro": exception_intro}
    finally:
        return success, rpc_data


async def fetch_response(req, language=""):
    """
    fetch url
    without json decode
    :param
        req: HTTPRequest object
        language: local-language
    :return: result
    """
    success = True
    response = ""
    try:
        if isinstance(req.headers, dict):
            req.headers["Sys-Language"] = language
        else:
            req.headers.add("Sys-Language", language)
        response = await AsyncHTTPClient().fetch(req)
        logging.info("tools origin response: %s" % response.body)
    except Exception as ex:
        success = False
        except_args = ex.args
        except_type = type(ex).__name__
        template = "An exception of type {0} occurred. Arguments:\n{1!r}"
        message = template.format(except_type, except_args)
        logging.debug("-----------%s" % message)
        if "Timeout" in except_args[1]:
            exception_type = "timeout"
            exception_intro = "==从远程获取数据失败"
        else:
            exception_type = "error"
            exception_intro = "==从远程获取数据失败"
        response = {"exception_type": exception_type, "exception_intro": exception_intro}
    finally:
        return success, response
