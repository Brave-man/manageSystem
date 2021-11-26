#! /usr/bin/env python
# -*- coding: utf-8 -*-
# __author__ = "David"
# Date  : 2021-11-22
# Digest:
import datetime

from pypika import Table, MySQLQuery as Query, Criterion, functions as fn, Order

from apps.base.service import BaseSqlService
from config.mdbConfig import DB_SYS
from tools.usual import calculate_password, generate_uid


class StudentService(BaseSqlService):
    """
    学生服务
    """
    DEFAULT_DB = DB_SYS
    DEFAULT_TABLE = "beacon_student"

    def query_userinfo(self, username):
        """
        查询用户基础信息
        :param username: 用户名
        :return:
        """
        table = Table(self.DEFAULT_TABLE)

        fields = ["student_uid", "student_name", "username", "password", "status"]
        where_list = [
            table.username == username
        ]

        q = Query.from_(table).select(
            *fields
        ).where(Criterion.all(where_list))

        result = self.fetchone(str(q))

        return result

    def add_student(self, student_name, username, password, class_uid, age=None):
        """
        添加学生
        :param student_name: 学生名称
        :param username: 用户名
        :param password: 密码
        :param age: 年龄
        :param class_uid: 班级uid
        :return:
        """

        student = self.query_userinfo(username)
        if not student:
            student_uid = generate_uid()

            create_args = {
                "student_uid": student_uid,
                "student_name": student_name,
                "username": username,
                "password": calculate_password(password),
                "age": age,
                "class_uid": class_uid
            }
            self.insert_one(data=create_args)
        else:
            student_uid = student["student_uid"]
            filter_args = {
                "student_uid": student_uid
            }
            upd_args = {
                "student_name": student_name,
                "username": username,
                "password": calculate_password(password),
                "age": age,
                "class_uid": class_uid,
                "updated": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
            self.update(filter_args, upd_args)

        return student_uid

    def query_student_list(self, class_uid, page=1, page_size=100, keyword=""):
        """
        查询班级学生列表
        :param class_uid: 班级uid
        :param page: 页数
        :param page_size: 每页条数
        :param keyword: 关键词
        :return:
        """
        offset = (page - 1) * page_size
        table = Table(self.DEFAULT_TABLE)

        fields = ["student_uid", "student_name", "age", "username"]
        where_list = [
            table.status == 1,
            table.class_uid == class_uid
        ]

        if keyword:
            where_list.append(table.student_name.like(f"%{keyword}%"))

        q = Query.from_(table).select(
            *fields
        ).where(Criterion.all(
            where_list
        )).orderby(
            table.created, order=Order.desc
        ).limit(page_size).offset(offset)

        result = self.fetchmany(str(q))
        return result

    def count_query_student_list(self, class_uid, page_size=100, keyword=""):
        """
        统计班级学生列表
        :param class_uid: 班级uid
        :param page_size: 每页条数
        :param keyword: 关键词
        :return:
        """
        table = Table(self.DEFAULT_TABLE)

        where_list = [
            table.class_uid == class_uid,
            table.status == 1
        ]

        if keyword:
            where_list.append(table.student_name.like(f"%{keyword}%"))

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

    def update_student(self, student_uid, upd_args):
        """
        更新学生
        :param student_uid: 学生uid
        :param upd_args: 更新内容
        :return:
        """
        if not upd_args.get("updated"):
            upd_args["updated"] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        filter_args = {
            "student_uid": student_uid
        }
        res = self.update(filter_args, upd_args)
        return res

    def query_students_by_student_uid_list(self, student_uid_list):
        """
        通过班级uid查询班级列表
        :param student_uid_list: 学生uid列表
        :return:
        """
        if not student_uid_list:
            return []

        table = Table(self.DEFAULT_TABLE)

        fields = ["student_uid", "student_name"]
        where_list = [
            table.student_uid.isin(student_uid_list),
        ]

        q = Query.from_(table).select(
            *fields
        ).where(Criterion.all(where_list))

        result = self.fetchmany(str(q))
        return result

    def query_profile(self, student_uid):
        """
        查询学生信息
        :param student_uid: 学生uid
        :return:
        """
        table = Table(self.DEFAULT_TABLE)

        fields = ["student_uid", "student_name"]
        where_list = [
            table.student_uid == student_uid,
        ]

        q = Query.from_(table).select(
            *fields
        ).where(Criterion.all(where_list))

        result = self.fetchone(str(q))
        return result
