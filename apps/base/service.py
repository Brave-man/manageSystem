# -*- coding: utf-8 -*-
"""
-------------------------------------------------
    File Name:   service
    Description: 
    Author:      wzj
    Date:        2019-10-28
-------------------------------------------------
    Change Activity:
-------------------------------------------------
"""

from copy import deepcopy
from dbdriver import mdb, sql
from config.mdbConfig import DB_SYS


class BaseService(object):
    """
    基础操作模块 普通累通常继承此类，方便自动获取数据库、缓存、等操作对象
    主要应用于业务代码即时实例化对象的类上，让这些动态使用的类，继承此类
    """
    DEFAULT_DB = DB_SYS

    def __init__(self, handler=None):
        """
        :param handler: RequestHandler
        """
        self.mdb = mdb
        self.sql = sql
        self.handler = handler

    def fetchone(self, sql, db=None):
        db = db or self.DEFAULT_DB
        return self.mdb[db].fetchone(sql)

    def fetchmany(self, sql, db=None):
        db = db or self.DEFAULT_DB
        return self.mdb[db].fetchmany(sql) or []

    def execute(self, sql, db=None):
        db = db or self.DEFAULT_DB
        return self.mdb[db].execute(sql)


class BaseSqlService(BaseService):
    """
    mysql基础服务
    """

    DEFAULT_DB = None
    DEFAULT_TABLE = None

    @staticmethod
    def _make_where_list(**kwargs):
        """
        组装where_list
        :param kwargs: { uuid_list: uuid 列表} 查询条件 _list 结尾会自动拼接 in 查询
        :return:
        """
        key_word = kwargs.pop("keyword", None)  # 关键字
        match_range = kwargs.pop("match_range", [])  # 关键字查询范围

        where_list = []
        if key_word and match_range:  # 模糊搜索
            sub_filter = [(key, key_word, "like", "or") for key in match_range]
            where_list.append(('query_str', sub_filter, 'sub', 'and'))

        for cl_key, value in kwargs.items():
            if value is not None:
                if cl_key.endswith("_list"):
                    # 多个 in 查询
                    real_key = cl_key.rstrip("_list")
                    if len(value) > 1:
                        where_list.append((real_key, tuple(value), "in", "and"))
                    elif len(value) == 1:
                        where_list.append((real_key, value[0], "=", "and"))
                    else:
                        pass
                else:
                    where_list.append((cl_key, value, "=", "and"))
        return where_list

    def insert_one(self, data: dict, db=None, table=None):
        """
        插入记录
        :param dict data: 待插入的记录dict
        :param table: 表名
        :param db: 库名
        :return:
        """
        db = db or self.DEFAULT_DB
        table = table or self.DEFAULT_TABLE
        sql_u = self.sql.insert(table, data)
        rows = self.execute(sql_u, db)
        return rows

    def insert_many(self, data_list: list, db=None, table=None):
        """
        批量插入数据
        :param data_list: 数据列表
        :param table: 表名
        :param db: 库名
        :return:
        """
        db = db or self.DEFAULT_DB
        table = table or self.DEFAULT_TABLE

        keys = tuple(data_list[0].keys())
        str_keys = "("
        length = len(keys)
        for index, key in enumerate(keys):
            str_keys += f"`{key}`"
            if index != (length - 1):
                str_keys += ","
            else:
                str_keys += ")"

        u_sql = f"insert into {table} {str_keys} values "

        value_li = []
        for data in data_list:
            values = tuple(data.values())
            str_v = f"{values}"
            if len(values) == 1:
                str_v = f"({values[0]})"

            value_li.append(str_v)
        value_str = ", ".join(value_li)

        u_sql += value_str
        rows = self.execute(u_sql, db)
        return rows

    def query(self, filter_args=None, key_list=None, order_by=None, db=None, table=None):
        """
        查询列表
        :param filter_args: { uuid_list: uuid 列表} 查询条件 _list 结尾会自动拼接 in 查询
        :param key_list: 查询的列
        :param order_by: 排序 [("created", "desc")]
        :param table: 表名
        :param db: 库名
        :return:
        """
        db = db or self.DEFAULT_DB
        table = table or self.DEFAULT_TABLE

        filter_args = {} if not filter_args else filter_args
        key_list = ["*"] if not key_list else key_list
        order_by = [("id", "ASC")] if not order_by else order_by

        filter_args = deepcopy(filter_args)
        page = filter_args.pop("page", 0)  # 第几页
        per_page = filter_args.pop("per_page", 1)  # 每页条数

        where_list = self._make_where_list(**filter_args)
        condition = {
            "where": where_list,
            "order": order_by
        }
        if page:
            limit_start = (page - 1) * per_page
            condition["limit"] = (limit_start, per_page)

        query_sql = self.sql.select(table, key_list, **condition)
        info_list = self.fetchmany(query_sql, db)

        return info_list

    def query_counts(self, filter_args=None, db=None, table=None):
        """
        查询条数
        :param filter_args: {key: value} 查询条件
        :param table: 表名
        :param db: 库名
        :return:
        """
        db = db or self.DEFAULT_DB
        table = table or self.DEFAULT_TABLE
        filter_args = {} if not filter_args else filter_args

        page_info = {
            "total": 0,
            "total_page": 0
        }

        filter_args = deepcopy(filter_args)
        filter_args.pop("page", 0)  # 第几页
        per_page = filter_args.pop("per_page", 1)  # 每页条数

        where_list = self._make_where_list(**filter_args)
        condition = {
            "where": where_list
        }

        count_sql = self.sql.select(table, ["count(id) AS counts"], **condition)
        count_info = self.fetchone(count_sql, db)
        total = count_info["counts"]

        if total:
            page_info = {
                "total": total,
                "total_page": divmod(total, per_page)[0] if divmod(total, per_page)[1] == 0 else
                divmod(total, per_page)[0] + 1
            }

        return page_info

    def get_detail(self, filter_args=None, key_list=None, order_by=None, db=None, table=None):
        """
        查询单条详情
        :param filter_args: {key: value} 查询条件
        :param key_list: 查询范围
        :param order_by: 排序 [("created", "desc")]
        :param table: 表名
        :param db: 库名
        :return:
        """
        db = db or self.DEFAULT_DB
        table = table or self.DEFAULT_TABLE
        filter_args = {} if not filter_args else filter_args
        key_list = ["*"] if not key_list else key_list
        order_by = [("id", "ASC")] if not order_by else order_by

        where_list = self._make_where_list(**filter_args)
        condition = {
            "where": where_list,
            "order": order_by
        }

        detail_sql = self.sql.select(table, key_list, **condition)
        detail_info = self.fetchone(detail_sql, db)
        return detail_info

    def update(self, filter_args, upd_info, db=None, table=None):
        """
        更新信息
        :param filter_args: {key: value} 查询条件
        :param upd_info: {} 更新内容
        :param table: 表名
        :param db: 库名
        :return:
        """
        db = db or self.DEFAULT_DB
        table = table or self.DEFAULT_TABLE

        condition = {
            "where": self._make_where_list(**filter_args),
        }
        sql_u = self.sql.update(table, upd_info, **condition)
        success = self.execute(sql_u, db)
        return success

    def delete(self, filter_args, db=None, table=None):
        """
        删除数据
        :param filter_args: {key: value} 查询条件
        :param table: 表名
        :param db: 库名
        :return:
        """
        pass
