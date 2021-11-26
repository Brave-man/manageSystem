#! /usr/bin/env python
# -*- coding: utf-8 -*-
# __author__ = "David"
# Date  : 2021-11-25
# Digest:

from abc import ABC

from apps.base.handler import BaseHandler
from apps.classes.classService import ClassService
from tools.error import BaseError, ArgError


class ClassHandler(BaseHandler, ABC):
    """
    班级查询
    """

    need_login = True

    async def get(self):
        """
        班级查询
        :return:
        """
        identity = self.identity
        if identity != "teacher":
            raise BaseError(msg="非法请求")

        page = self.get_int_argument("page", 1)
        page_size = self.get_int_argument("page_size", 100)
        keyword = self.get_str_argument("keyword", "")

        # 查询班级列表
        class_obj = ClassService()
        class_list = class_obj.query_classes_list(page, page_size, keyword)
        total, total_page = class_obj.count_query_classes_list(page_size, keyword)

        data = {
            "total": total,
            "total_page": total_page,
            "class_list": class_list
        }
        self.simplewrite(data=data)

    async def post(self):
        """
        添加班级
        :return:
        """
        identity = self.identity
        if identity != "teacher":
            raise BaseError(msg="非法请求")

        class_name = self.get_body_argument("class_name")
        if not class_name:
            raise ArgError(msg="class_name为必填参数")

        # 添加班级
        class_obj = ClassService()
        class_uid = class_obj.add_class(class_name)

        data = {
            "class_uid": class_uid
        }
        self.simplewrite(data=data)

    async def put(self):
        """
        更新班级
        :return:
        """
        identity = self.identity
        if identity != "teacher":
            raise BaseError(msg="非法请求")

        class_uid = self.get_body_argument("class_uid")
        class_name = self.get_body_argument("class_name", None)

        class_obj = ClassService()
        exist_class = class_obj.query_class_by_class_name(class_name)
        if exist_class:
            if exist_class["class_uid"] == class_uid:
                self.simplewrite()
                return

            raise BaseError(msg="该班级名称与已存在的班级名称重复")

        upd_args = {}
        if class_name:
            upd_args["class_name"] = class_name

        if not upd_args:
            self.simplewrite()
            return

        # 更新班级
        result = class_obj.update_class(class_uid, upd_args)
        if result:
            self.simplewrite()
        else:
            self.simplewrite(code=0, msg="更新失败")

    async def delete(self):
        """
        删除班级
        :return:
        """
        identity = self.identity
        if identity != "teacher":
            raise BaseError(msg="非法请求")

        class_uid = self.get_body_argument("class_uid")

        class_obj = ClassService()
        result = class_obj.update_class(class_uid, {"status": 0})
        if result:
            self.simplewrite()
        else:
            self.simplewrite(code=0, msg="删除失败")
