# -*- coding: utf-8 -*-
# @Time    : 2019/08/20 下午1:54
# @Author  : Sean
# @Site    : beacon_business
# @Software: PyCharm

import re
import logging


class SqlHandlers(object):
    """以参数的形式重组sql"""

    # ----------------------------------------------------------------------
    def __init__(self):
        """Constructor"""
        __key__ = "meidaitech"

    # ----------------------------------------------------------------------
    def _setDb(self, db):
        """"""
        self.db = db

    # ----------------------------------------------------------------------
    def _select(self, table_name, keyList, **kwargs):
        """
        table_name: 表名
        keyList: 查询字段列表
        kwargs: 条件参数

        """
        keys = ",".join(keyList)
        sql = "select %s from %s" % (keys, table_name)
        getSql = self.__buildSql(sql, **kwargs)
        getSql = self.__sqlfix(getSql)
        return getSql

    def select(self, table_name, keyList, **kwargs):
        """
        table_name: 表名
        keyList: 查询字段列表
        kwargs: 条件参数

        """
        return self._select(table_name, keyList, **kwargs)

    # ----------------------------------------------------------------------
    def _insert(self, table_name, keyDict, ON_DUPLICATE_KEY_UPDATE=None):
        """
        table_name: 表名
        keyDict: 参数字典
        kwargs: 条件参数
        """
        keys = ",".join(keyDict.keys())
        valueList = []
        for value in keyDict.values():
            if (isinstance(value, type("string")) or isinstance(value, type(u"unicode"))) and value != "now()":
                valueList.append("'%s'" % value.replace("'", "''"))
            else:
                valueList.append(str(value))
        values = ",".join(valueList)
        sql = "insert into %s (%s) values (%s)" % (table_name, keys, values)
        if ON_DUPLICATE_KEY_UPDATE:
            vs = []
            for key, value in ON_DUPLICATE_KEY_UPDATE.items():
                if (isinstance(value, type("string")) or isinstance(value, type(u"unicode"))) and value != "now()":
                    vs.append("`%s`='%s'" % (key, value.replace("'", "''")))
                else:
                    vs.append("`%s`=%s" % (key, str(value)))
            sql = sql + ' ON DUPLICATE KEY UPDATE ' + ','.join(vs)
        sql = self.__sqlfix(sql)
        return sql

    def insert(self, table_name, keyDict, ON_DUPLICATE_KEY_UPDATE=None):
        """
        table_name: 表名
        keyDict: 参数字典
        kwargs: 条件参数
        """
        return self._insert(table_name, keyDict, ON_DUPLICATE_KEY_UPDATE)

    # ----------------------------------------------------------------------

    def _update(self, table_name, keyDict, **kwargs):
        """
        更新语句重组
        table_name: 表名
        keyDict: 参数字典
        kwargs: 条件参数
        """
        setList = self._setUpdateParam(keyDict)
        if not setList:
            return None
        setData = ",".join(setList)
        sql = "update %s set %s" % (table_name, setData)
        getSql = self.__buildSql(sql, **kwargs)
        getSql = self.__sqlfix(getSql)
        return getSql

    def update(self, table_name, keyDict, **kwargs):
        """
        更新语句重组
        table_name: 表名
        keyDict: 参数字典
        kwargs: 条件参数
        """
        return self._update(table_name, keyDict, **kwargs)

    # ----------------------------------------------------------------------

    def _delete(self):
        """删除语句重组"""
        pass

    def delete(self):
        """删除语句重组"""
        return self._delete()

    # ----------------------------------------------------------------------
    def _setUpdateParam(self, keyDict):
        """"""
        paramList = []
        for key, value in keyDict.items():
            if type(value) in [int, float] or value in ["now()", "NOW()"]:
                data = "%s=%s" % (key, value)
            else:
                data = "%s='%s'" % (key, value.replace("'", "\\'"))
            paramList.append(data)
        return paramList

    def __sqlfix(self, sql):
        """
        转义特殊字符
        """
        sql = re.sub(r"(?<!%)%(?!%)", "%%", sql)
        sql = re.sub(r"(?<!\\)\\(?!\\)", r"\\\\", sql)
        return sql

    # ----------------------------------------------------------------------
    def __where(self, params):
        """
        where条件:
        params: [(key, value, way, mode),(key, value, way, mode),...]
        way: "=", "!=", "like", ">", "<", "sub"
        mode: "and", "or"
        """
        if params:
            last_condition = list(params[-1])
            last_condition[-1] = ''
            params[-1] = tuple(last_condition)
        whereList = []
        for param in params:
            key, value, way, mode = param
            if isinstance(value, str):
                value = value.replace("'", "''")
            if way == "like":
                data = "`%s` %s '%%%%%s%%%%'" % (key, way, value)
            elif way in ["in", "not in"]:
                if isinstance(value, (list, tuple)):
                    value_s = [str(item) for item in value]
                    if any(map(lambda i: isinstance(value[0], str), value)):
                        # 有任何一个字符类型
                        in_where = "('" + "','".join(value) + "')"
                    else:
                        in_where = "(" + ','.join(value_s) + ")"
                else:
                    in_where = value
                data = "`%s` in %s" % (key, in_where)
            elif way == "between":
                data = "`%s` %s %s" % (key, way, "'{}' and '{}'".format(value[0], value[1]))
            elif way == "sub":
                # way == "sub" 表示子条件 需要括号包围
                data = "(%s)" % self.__where(value)
            else:
                if isinstance(value, int):
                    data = "`%s` %s %d" % (key, way, value)
                else:
                    data = "`%s` %s '%s'" % (key, way, value)
            if mode:
                data += " %s" % mode
            whereList.append(data)
        setWhere = " ".join(whereList)
        if setWhere.endswith(('and', 'or', 'AND', 'OR')):
            rindex = setWhere.rindex(' ')
            setWhere = setWhere[:rindex or len(setWhere)]
        return setWhere

    # ----------------------------------------------------------------------
    def __order(self, params):
        """
        降序与升序
        params: [(key, desc), (kes2, asc)...]
        key: 表示数据库字段
        """
        if isinstance(params, str):
            return params
        setList = []
        for param in params:
            setList.append(" ".join(param))
        return ",".join(setList)

    # ----------------------------------------------------------------------
    def __buildSql(self, sql, **kwargs):
        """
        {
           "where":__where,
           "limit": "__limit",
           "order": "__order",
           "group": "__group",
           "having": "__having",
        }
        """
        if kwargs.get("where", None):
            sql = "%s where %s" % (sql, self.__where(kwargs["where"]))
        if kwargs.get('group'):
            groups = "group by %s" % kwargs['group']
            sql = "%s %s" % (sql, groups)
        if kwargs.get("order", None):
            order = "order by %s" % self.__order(kwargs["order"])
            sql = "%s %s" % (sql, order)
        if kwargs.get("limit", None):
            limits = "limit %d, %d" % kwargs["limit"]
            sql = "%s %s" % (sql, limits)
        return sql

    def paginate(self, page: int, paginate_by: int = 20):
        if page > 0:
            page -= 1
        return page * paginate_by, paginate_by
