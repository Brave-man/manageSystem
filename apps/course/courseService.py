#! /usr/bin/env python
# -*- coding: utf-8 -*-
# __author__ = "David"
# Date  : 2021-11-25
# Digest:

import datetime

from pypika import Table, MySQLQuery as Query, Criterion, Order, functions as fn

from apps.base.service import BaseSqlService
from tools.usual import generate_uid
from config.mdbConfig import DB_SYS


class CourserService(BaseSqlService):
    """
    课程服务
    """
    DEFAULT_DB = DB_SYS
    DEFAULT_TABLE = "beacon_course"

    def query_courses_by_course_uid_list(self, course_uid_list):
        """
        通过课程uid查询课程
        :param course_uid_list:课程uid列表
        :return:
        """
        if not course_uid_list:
            return []

        table = Table(self.DEFAULT_TABLE)

        fields = ["course_uid", "course_name"]
        where_list = [
            table.course_uid.isin(course_uid_list),
        ]

        q = Query.from_(table).select(
            *fields
        ).where(Criterion.all(where_list))

        result = self.fetchmany(str(q))
        return result

    def query_course_exist(self, teacher_uid, class_uid, course_name, status=None):
        """
        查询课程是否已存在
        :param teacher_uid: 老师uid
        :param class_uid: 班级uid
        :param course_name: 课程名称
        :param status: 状态
        :return:
        """
        table = Table(self.DEFAULT_TABLE)

        fields = ["course_uid"]
        where_list = [
            table.teacher_uid == teacher_uid,
            table.class_uid == class_uid,
            table.course_name == course_name,
        ]

        if status is not None:
            where_list.append(table.status == status)

        q = Query.from_(table).select(
            *fields
        ).where(Criterion.all(where_list))

        result = self.fetchone(str(q))
        return result

    def add_course(self, teacher_uid, class_uid, course_name):
        """
        添加课程
        :param teacher_uid: 老师uid
        :param class_uid: 班级uid
        :param course_name: 课程名称
        :return:
        """
        course = self.query_course_exist(teacher_uid, class_uid, course_name)
        if not course:
            course_uid = generate_uid()
            create_args = {
                "course_uid": course_uid,
                "teacher_uid": teacher_uid,
                "class_uid": class_uid,
                "course_name": course_name,
                "status": 1
            }
            self.insert_one(data=create_args)
        else:
            course_uid = course["course_uid"]
            filter_args = {
                "course_uid": course_uid
            }
            upd_args = {
                "teacher_uid": teacher_uid,
                "class_uid": class_uid,
                "course_name": course_name,
                "status": 1,
                "updated": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
            self.update(filter_args, upd_args)

        return course_uid

    def query_course_list(self, teacher_uid, page=1, page_size=100, keyword=""):
        """
        查询课程列表
        :param teacher_uid: 老师uid
        :param page: 页数
        :param page_size: 每页条数
        :param keyword: 关键词
        :return:
        """
        offset = (page - 1) * page_size
        table = Table(self.DEFAULT_TABLE)

        fields = ["course_uid", "course_name", "class_uid"]
        where_list = [
            table.teacher_uid == teacher_uid,
            table.status == 1
        ]

        if keyword:
            where_list.append(table.course_name.like(f"%{keyword}%"))

        q = Query.from_(table).select(
            *fields
        ).where(Criterion.all(
            where_list
        )).orderby(
            table.created, order=Order.desc
        ).limit(page_size).offset(offset)

        result = self.fetchmany(str(q))
        return result

    def count_query_course_list(self, teacher_uid, page_size=100, keyword=""):
        """
        统计课程列表
        :param teacher_uid: 老师uid
        :param page_size: 每页条数
        :param keyword: 关键词
        :return:
        """
        table = Table(self.DEFAULT_TABLE)

        where_list = [
            table.teacher_uid == teacher_uid,
            table.status == 1
        ]

        if keyword:
            where_list.append(table.course_name.like(f"%{keyword}%"))

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

    def update_course(self, course_uid, teacher_uid, upd_args):
        """
        更新课程
        :param course_uid: 课程uid
        :param teacher_uid: 老师uid
        :param upd_args: 更新内容
        :return:
        """
        filter_args = {
            "course_uid": course_uid,
            "teacher_uid": teacher_uid,
        }

        if not upd_args.get("updated"):
            upd_args["updated"] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        result = self.update(filter_args, upd_args)
        return result
