#! /usr/bin/env python
# -*- coding: utf-8 -*-
# __author__ = "David"
# Date  : 2021-11-22
# Digest:

from pypika import Table, MySQLQuery as Query, Criterion

from apps.base.service import BaseSqlService
from config.mdbConfig import DB_SYS


class TeacherService(BaseSqlService):
    """
    教师服务
    """
    DEFAULT_DB = DB_SYS
    DEFAULT_TABLE = "beacon_teacher"

    def query_userinfo(self, username):
        """
        查询用户基础信息
        :param username: 用户名
        :return:
        """
        table = Table(self.DEFAULT_TABLE)

        fields = ["teacher_uid", "teacher_name", "username", "password"]
        where_list = [
            table.username == username
        ]

        q = Query.from_(table).select(
            *fields
        ).where(Criterion.all(where_list))

        result = self.fetchone(str(q))

        return result

    def query_profile(self, teacher_uid):
        """
        查询老师信息
        :param teacher_uid: 老师uid
        :return:
        """
        table = Table(self.DEFAULT_TABLE)

        fields = ["teacher_uid", "teacher_name"]
        where_list = [
            table.teacher_uid == teacher_uid,
        ]

        q = Query.from_(table).select(
            *fields
        ).where(Criterion.all(where_list))

        result = self.fetchone(str(q))
        return result
