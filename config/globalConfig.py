# -*- coding: utf-8 -*-
# @Time    : 2019/08/20 下午1:54
# @Author  : Sean
# @Site    : beacon_business
# @Software: PyCharm

import os

DEBUG = True
SERVER_NAME = "manageSystem"
server_name = SERVER_NAME
static_url_prefix = "/static/"
static_path = os.path.join(os.path.abspath("."), "static/")
template_path = os.path.join(os.path.abspath("."), "templates/")

# 默认登录有效期 单位:天
LOGIN_EXPIRE_DAY = 365

# md5加密key
MD5_KEY = "234$2@1"