#! /usr/bin/env python
# -*- coding: utf-8 -*-
# __author__ = "David"
# Date  : 2021-11-25
# Digest: 成绩

from abc import ABC

from apps.base.handler import BaseHandler
from apps.score.scoreService import ScoreService
from apps.course.courseService import CourserService
from apps.user.studentService import StudentService
from tools.error import BaseError, ArgError


class StudentScoreHandler(BaseHandler, ABC):
    """
    学生成绩查询
    """

    need_login = True

    async def get(self):
        """
        学生成绩查询
        :return:
        """
        identity = self.identity
        user_uid = self.user_uid
        if identity != "student":
            raise BaseError(msg="非法请求")

        page = self.get_int_argument("page", 1)
        page_size = self.get_int_argument("page_size", 20)

        # 查询学生成绩
        score_obj = ScoreService()
        course_list = score_obj.query_student_courses_by_student_uid(user_uid, page, page_size)
        total, total_page = score_obj.count_query_student_courses_by_student_uid(user_uid, page_size)

        course_map = {}
        if course_list:
            # 查询课程名称
            course_uid_list = {course["course_uid"] for course in course_list}
            course_obj = CourserService()
            courses = course_obj.query_courses_by_course_uid_list(course_uid_list)
            course_map = dict([(course["course_uid"], course["course_name"]) for course in courses])

        data = {
            "total": total,
            "total_page": total_page,
            "course_list": self.format_course_list(course_list, course_map)
        }
        self.simplewrite(data=data)

    @staticmethod
    def format_course_list(course_list, course_map):
        """
        格式化课程列表
        :param course_list: 课程列表
        :param course_map: 课程map
        :return:
        """
        for course in course_list:
            course_uid = course["course_uid"]
            course["course_name"] = course_map.get(course_uid, "")

        return course_list


class TeacherScoreHandler(BaseHandler, ABC):
    """
    老师对学生成绩管理
    """
    need_login = True

    async def post(self):
        """
        录入成绩
        :return:
        """
        identity = self.identity
        if identity != "teacher":
            raise BaseError(msg="非法请求")

        course_uid = self.get_body_argument("course_uid")
        student_uid = self.get_body_argument("student_uid")
        score = self.get_body_argument("score")

        # 录入成绩
        score_obj = ScoreService()
        result = score_obj.add_score(course_uid, student_uid, score)
        if result:
            self.simplewrite()
        else:
            self.simplewrite(code=0, msg="录入失败")

    async def get(self):
        """
        成绩查询
        :return:
        """
        identity = self.identity
        if identity != "teacher":
            raise BaseError(msg="非法请求")

        course_uid = self.get_str_argument("course_uid")
        page = self.get_int_argument("page", 1)
        page_size = self.get_int_argument("page_size", 20)
        order_type = self.get_str_argument("order_type", "DESC")

        if order_type not in ["ASC", "DESC"]:
            raise ArgError(msg="order_type参数非法")

        # 课程查询成绩
        score_obj = ScoreService()
        score_list = score_obj.query_course_student_scores(course_uid, page, page_size, order_type)
        total, total_page = score_obj.count_query_course_student_scores(course_uid, page_size)

        student_map = {}
        if score_list:
            # 查询学生名称
            student_uid_list = {score["student_uid"] for score in score_list}

            student_obj = StudentService()
            student_list = student_obj.query_students_by_student_uid_list(student_uid_list)
            student_map = dict([(student["student_uid"], student["student_name"]) for student in student_list])

        data = {
            "total": total,
            "total_page": total_page,
            "score_list": self.format_score_list(score_list, student_map)
        }
        self.simplewrite(data=data)

    @staticmethod
    def format_score_list(score_list, student_map):
        """
        格式化课程列表
        :param score_list: 成绩列表
        :param student_map: 课程map
        :return:
        """
        for score in score_list:
            student_uid = score["student_uid"]
            score["student_name"] = student_map.get(student_uid, "")

        return score_list

    async def put(self):
        """
        更新成绩
        :return:
        """
        identity = self.identity
        if identity != "teacher":
            raise BaseError(msg="非法请求")

        course_uid = self.get_body_argument("course_uid")
        student_uid = self.get_body_argument("student_uid")
        score = self.get_body_argument("score")

        # 更新成绩
        score_obj = ScoreService()
        result = score_obj.update_student_score(course_uid, student_uid, score)
        if result:
            self.simplewrite()
        else:
            self.simplewrite(code=0, msg="更新失败")
