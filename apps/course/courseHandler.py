#! /usr/bin/env python
# -*- coding: utf-8 -*-
# __author__ = "David"
# Date  : 2021-11-25
# Digest:

from abc import ABC

from apps.base.handler import BaseHandler
from apps.course.courseService import CourserService
from apps.classes.classService import ClassService
from tools.error import BaseError


class CourseHandler(BaseHandler, ABC):
    """
    课程管理
    """

    need_login = True

    async def post(self):
        """
        创建课程
        :return:
        """
        identity = self.identity
        if identity != "teacher":
            raise BaseError(msg="非法请求")

        teacher_uid = self.user_uid
        course_name = self.get_body_argument("course_name")  # 课程uid
        class_uid = self.get_body_argument("class_uid")  # 班级uid

        course_obj = CourserService()
        exist = course_obj.query_course_exist(teacher_uid, class_uid, course_name, status=1)
        if exist:
            self.simplewrite()
            return

        # 添加课程
        course_uid = course_obj.add_course(teacher_uid, class_uid, course_name)
        data = {
            "course_uid": course_uid
        }
        self.simplewrite(data=data)

    async def get(self):
        """
        查询课程列表
        :return:
        """
        identity = self.identity
        if identity != "teacher":
            raise BaseError(msg="非法请求")

        teacher_uid = self.user_uid
        page = self.get_int_argument("page", 1)
        page_size = self.get_int_argument("page_size", 20)
        keyword = self.get_str_argument("keyword", "")

        course_obj = CourserService()
        course_list = course_obj.query_course_list(teacher_uid, page, page_size, keyword)
        total, total_page = course_obj.count_query_course_list(teacher_uid, page_size, keyword)

        class_map = {}
        if course_list:
            class_obj = ClassService()
            class_uid_list = {course["class_uid"] for course in course_list}
            class_list = class_obj.query_class_by_class_uid_list(list(class_uid_list))
            class_map = dict([(item["class_uid"], item["class_name"]) for item in class_list])

        data = {
            "total": total,
            "total_page": total_page,
            "course_list": self.format_course_list(course_list, class_map)
        }
        self.simplewrite(data=data)

    @staticmethod
    def format_course_list(course_list, class_map):
        """
        格式化课程列表
        :param course_list: 课程列表
        :param class_map: 班级map
        :return:
        """
        for course in course_list:
            class_uid = course["class_uid"]
            course["class_name"] = class_map.get(class_uid, "")

        return course_list

    async def put(self):
        """
        更新课程
        :return:
        """
        identity = self.identity
        if identity != "teacher":
            raise BaseError(msg="非法请求")

        teacher_uid = self.user_uid
        course_uid = self.get_body_argument("course_uid")
        course_name = self.get_body_argument("course_name")
        class_uid = self.get_body_argument("class_uid")

        upd_args = {}
        if course_name:
            upd_args["course_name"] = course_name

        if class_uid:
            upd_args["class_uid"] = class_uid

        # 更新课程
        course_obj = CourserService()
        result = course_obj.update_course(course_uid, teacher_uid, upd_args)
        if result:
            self.simplewrite()
        else:
            self.simplewrite(code=0, msg="更新失败")
