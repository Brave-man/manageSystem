# -*- coding: utf-8 -*-
"""
-------------------------------------------------
    File Name:   __init__.py
    Description: 数据库驱动相关包
    Author:      wzj
    Date:        2019-09-26
-------------------------------------------------
    Change Activity:
-------------------------------------------------
"""

from config.mdbConfig import mdb_configs

from .mysqlPool import MultiMdbconn
from .mysqlBuilder import SqlHandlers

mdb = MultiMdbconn(mdb_configs)
sql = SqlHandlers()
