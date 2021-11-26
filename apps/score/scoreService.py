#! /usr/bin/env python
# -*- coding: utf-8 -*-
# __author__ = "David"
# Date  : 2021-11-25
# Digest:

import datetime

from pypika import Table, MySQLQuery as Query, Criterion, Order, functions as fn

from apps.base.service import BaseSqlService
from config.mdbConfig import DB_SYS


class ScoreService(BaseSqlService):
    """
    成绩服务
    """
    DEFAULT_DB = DB_SYS
    DEFAULT_TABLE = "beacon_score"

    def query_student_courses_by_student_uid(self, student_uid, page=1, page_size=100):
        """
        查询学生课程成绩
        :param student_uid: 学生uid
        :param page: 页数
        :param page_size: 每页条数
        :return:
        """
        offset = (page - 1) * page_size
        table = Table(self.DEFAULT_TABLE)

        fields = ["course_uid", "score"]
        where_list = [
            table.student_uid == student_uid,
            table.status == 1
        ]

        q = Query.from_(table).select(
            *fields
        ).where(Criterion.all(
            where_list
        )).orderby(
            table.created, order=Order.desc
        ).limit(page_size).offset(offset)

        result = self.fetchmany(str(q))
        return result

    def count_query_student_courses_by_student_uid(self, student_uid, page_size=100):
        """
        查询学生课程成绩
        :param student_uid: 学生uid
        :param page_size: 每页条数
        :return:
        """
        table = Table(self.DEFAULT_TABLE)

        where_list = [
            table.student_uid == student_uid,
            table.status == 1
        ]

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

    def check_score_exist(self, course_uid, student_uid):
        """
        检查成绩是否存在
        :param course_uid: 课程uid
        :param student_uid: 学生uid
        :return:
        """
        table = Table(self.DEFAULT_TABLE)

        where_list = [
            table.student_uid == student_uid,
            table.course_uid == course_uid
        ]

        q = Query.from_(table).select(
            table.course_uid
        ).where(Criterion.all(
            where_list
        ))

        result = self.fetchone(str(q))
        return result

    def add_score(self, course_uid, student_uid, score):
        """
        录入成绩
        :param course_uid: 课程uid
        :param student_uid: 学生uid
        :param score: 成绩
        :return:
        """
        score_record = self.check_score_exist(course_uid, student_uid)
        if not score_record:
            create_args = {
                "course_uid": course_uid,
                "student_uid": student_uid,
                "score": score,
                "status": 1
            }
            result = self.insert_one(create_args)
        else:
            filter_args = {
                "course_uid": course_uid,
                "student_uid": student_uid,
            }
            upd_args = {
                "score": score,
                "status": 1,
                "updated": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
            result = self.update(filter_args, upd_args)

        return result

    def query_course_student_scores(self, course_uid, page=1, page_size=100, order_type="DESC"):
        """
        查询课程的学生成绩
        :param course_uid: 课程uid
        :param page: 页数
        :param page_size: 每页条数
        :param order_type: 成绩排序方式
        :return:
        """
        offset = (page - 1) * page_size
        table = Table(self.DEFAULT_TABLE)

        fields = ["course_uid", "student_uid", "score"]
        where_list = [
            table.course_uid == course_uid,
            table.status == 1
        ]

        q = Query.from_(table).select(
            *fields
        ).where(Criterion.all(
            where_list
        )).orderby(
            table.score, order=Order(order_type)
        ).limit(page_size).offset(offset)

        result = self.fetchmany(str(q))
        return result

    def count_query_course_student_scores(self, course_uid, page_size=100):
        """
        查询学生课程成绩
        :param course_uid: 课程uid
        :param page_size: 每页条数
        :return:
        """
        table = Table(self.DEFAULT_TABLE)

        where_list = [
            table.course_uid == course_uid,
            table.status == 1
        ]

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

    def update_student_score(self, course_uid, student_uid, score):
        """
        更新学生成绩
        :param course_uid: 课程uid
        :param student_uid: 学生uid
        :param score: 成绩
        :return:
        """
        filter_args = {
            "course_uid": course_uid,
            "student_uid": student_uid,
        }
        upd_args = {
            "score": score,
            "updated": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        res = self.update(filter_args, upd_args)
        return res
