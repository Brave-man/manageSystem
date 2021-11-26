#! /usr/bin/env python
# -*- coding: utf-8 -*-
# __author__ = "David"
# Date  : 2021-11-25
# Digest:
import datetime

from pypika import Table, MySQLQuery as Query, Criterion, Order, functions as fn

from apps.base.service import BaseSqlService
from config.mdbConfig import DB_SYS
from tools.usual import generate_uid


class ClassService(BaseSqlService):
    """
    班级 服务
    """
    DEFAULT_DB = DB_SYS
    DEFAULT_TABLE = "beacon_class"

    def query_class_by_class_uid_list(self, class_uid_list):
        """
        通过班级uid查询班级列表
        :param class_uid_list:班级uid列表
        :return:
        """
        if not class_uid_list:
            return []

        table = Table(self.DEFAULT_TABLE)

        fields = ["class_uid", "class_name"]
        where_list = [
            table.class_uid.isin(class_uid_list),
        ]

        q = Query.from_(table).select(
            *fields
        ).where(Criterion.all(where_list))

        result = self.fetchmany(str(q))
        return result

    def query_classes_list(self, page=1, page_size=100, keyword=""):
        """
        查询班级列表
        :param page: 页数
        :param page_size: 每页条数
        :param keyword: 关键词
        :return:
        """
        offset = (page - 1) * page_size
        table = Table(self.DEFAULT_TABLE)

        fields = ["class_uid", "class_name"]
        where_list = [
            table.status == 1
        ]

        if keyword:
            where_list.append(table.class_name.like(f"%{keyword}%"))

        q = Query.from_(table).select(
            *fields
        ).where(Criterion.all(
            where_list
        )).orderby(
            table.created, order=Order.desc
        ).limit(page_size).offset(offset)

        result = self.fetchmany(str(q))
        return result

    def count_query_classes_list(self, page_size=100, keyword=""):
        """
        统计班级列表
        :param page_size: 每页条数
        :param keyword: 关键词
        :return:
        """
        table = Table(self.DEFAULT_TABLE)

        where_list = [
            table.status == 1
        ]

        if keyword:
            where_list.append(table.class_name.like(f"%{keyword}%"))

        q = Query.from_(table).select(
            fn.Count("*").as_("counts")
        ).where(Criterion.all(
            where_list
        ))

        count_info = self.fetchone(q.get_sql())
        total = count_info.get("counts", 0)
        quotient, remainder = divmod(total, page_size)
        total_page = quotient if remainder == 0 else quotient + 1

        return total, total_page

    def query_class_by_class_name(self, class_name):
        """
        查询班级
        :param class_name: 班级名称
        :return:
        """
        table = Table(self.DEFAULT_TABLE)

        fields = ["class_uid", "class_name", "status"]
        where_list = [
            table.class_name == class_name
        ]

        q = Query.from_(table).select(
            *fields
        ).where(Criterion.all(
            where_list
        ))

        result = self.fetchone(str(q))
        return result

    def add_class(self, class_name):
        """
        添加班级
        :param class_name: 班级名称
        :return:
        """
        result = self.query_class_by_class_name(class_name)
        if not result:
            class_uid = generate_uid()
            insert_args = {
                "class_uid": class_uid,
                "class_name": class_name
            }
            self.insert_one(data=insert_args)
        else:
            class_uid = result["class_uid"]
            if result["status"] != 1:
                filter_args = {
                    "class_uid": class_uid
                }
                upd_args = {
                    "status": 1
                }
                self.update(filter_args, upd_args)

        return class_uid

    def update_class(self, class_uid, upd_args):
        """
        更新班级
        :param class_uid: 班级uid
        :param upd_args: 更新内容
        :return:
        """
        if not upd_args.get("updated"):
            upd_args["updated"] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        filter_args = {
            "class_uid": class_uid
        }
        res = self.update(filter_args, upd_args)
        return res
