#! /usr/bin/env python
# -*- coding: utf-8 -*-
# __author__ = "David"
# Date  : 2021-11-25
# Digest:

from abc import ABC

from apps.base.handler import BaseHandler
from apps.user.studentService import StudentService
from tools.error import BaseError, ArgError
from tools.usual import calculate_password


class StudentHandler(BaseHandler, ABC):
    """
    学生管理
    """

    need_login = True

    async def post(self):
        """
        创建学生
        :return:
        """
        identity = self.identity
        if identity != "teacher":
            raise BaseError(msg="非法请求")

        student_name = self.get_body_argument("student_name")
        username = self.get_body_argument("username", "")
        password = self.get_body_argument("password", "123456")
        class_uid = self.get_body_argument("class_uid")
        age = self.get_body_argument("age", None)

        if not student_name:
            raise ArgError(msg="学生姓名为必填参数")

        if not username:
            username = student_name

        # 检查学生是否存在
        student_obj = StudentService()
        exist = student_obj.query_userinfo(username)
        if exist:
            raise ArgError(msg="该学生已存在")

        # 添加学生
        student_uid = student_obj.add_student(student_name, username, password, class_uid, age)
        data = {
            "student_uid": student_uid
        }
        self.simplewrite(data=data)

    async def get(self):
        """
        查询学生列表
        :return:
        """
        identity = self.identity
        if identity != "teacher":
            raise BaseError(msg="非法请求")

        class_uid = self.get_str_argument("class_uid")
        page = self.get_int_argument("page", 1)
        page_size = self.get_int_argument("page_size", 20)
        keyword = self.get_str_argument("keyword", "")

        # 查询学生列表
        student_obj = StudentService()
        student_list = student_obj.query_student_list(class_uid, page, page_size, keyword)
        total, total_page = student_obj.count_query_student_list(class_uid, page_size, keyword)

        data = {
            "total": total,
            "total_page": total_page,
            "student_list": student_list
        }
        self.simplewrite(data=data)

    async def put(self):
        """
        更新学生信息
        :return:
        """
        identity = self.identity
        if identity != "teacher":
            raise BaseError(msg="非法请求")

        student_uid = self.get_body_argument("student_uid")
        student_name = self.get_body_argument("student_name", None)
        class_uid = self.get_body_argument("class_uid", None)
        username = self.get_body_argument("username", None)
        password = self.get_body_argument("password", None)
        age = self.get_body_argument("age", None)

        student_obj = StudentService()
        exist = student_obj.query_userinfo(username)
        if exist:
            exist_student_uid = exist["student_uid"]
            if username and exist_student_uid != student_uid:
                raise ArgError(msg="修改的用户名与已存在的学生冲突")

        upd_args = {}
        if student_name:
            upd_args["student_name"] = student_name

        if class_uid:
            upd_args["class_uid"] = class_uid

        if username:
            upd_args["username"] = username

        if password:
            upd_args["password"] = calculate_password(password)

        if age is not None:
            upd_args["age"] = age

        if not upd_args:
            self.simplewrite()
            return

        # 更新学生信息
        result = student_obj.update_student(student_uid, upd_args)
        if result:
            self.simplewrite()
        else:
            self.simplewrite(code=0, msg="更新失败")

    async def delete(self):
        """
        删除学生信息
        :return:
        """
        identity = self.identity
        if identity != "teacher":
            raise BaseError(msg="非法请求")

        student_uid = self.get_body_argument("student_uid")

        # 删除学生信息
        student_obj = StudentService()
        result = student_obj.update_student(student_uid, {"status": 0})
        if result:
            self.simplewrite()
        else:
            self.simplewrite(code=0, msg="更新失败")
