# -*- coding: utf-8 -*-
# @Time    : 2019/08/20 下午1:54
# @Author  : Sean
# @Site    : beacon_business
# @Software: PyCharm

import logging
import traceback
import MySQLdb
from dbutils.pooled_db import PooledDB


class MysqlManager(object):
    """
    mysql 操作对象
    """
    def __init__(self, conn_conf, pool_conf=None):
        """
        初始化一个 pool
        :param conn_conf: mysql 链接配置参数
        :param pool_conf: pool 配置参数
        """
        self.host = conn_conf["host"]
        self.port = conn_conf["port"]
        self.pwd = conn_conf["pwd"]
        self.user = conn_conf["user"]
        self.db = conn_conf["db"]
        self.__transaction = {}     # transaction
        self.__transaction_cur = {}
        pool_conf = pool_conf or {}
        self.Pool = PooledDB(creator=MySQLdb, mincached=pool_conf.get("mincached", 2),
                             maxcached=pool_conf.get("maxcached", 4),
                             maxshared=pool_conf.get("maxshared", 0),
                             maxconnections=pool_conf.get("maxconnections", 4),
                             blocking=True,
                             host=self.host, port=self.port, user=self.user, password=self.pwd, database=self.db,
                             charset="utf8mb4")

    def _getConnectCur(self):
        self.conn = self.Pool.connection()
        cur = self.conn.cursor(cursorclass=MySQLdb.cursors.DictCursor)
        if not cur:
            return None
        else:
            return cur

    def fetchmany(self, sql):
        """
        fetch all
        :param sql:
        :return:
        """
        relist = []
        cur = self._getConnectCur()
        try:
            logging.info("SQL---: {}".format(sql))
            cur.execute(sql)
            relist = cur.fetchall()
            relist = list(relist)
        except BaseException:
            logging.error("SQL ERROR: {}".format(traceback.format_exc()))
        finally:
            cur.close()
            self.conn.close()
        return relist

    def fetchone(self, sql):
        """
        查询单条
        :param sql:
        :return:
        """
        relist = None
        cur = self._getConnectCur()
        try:
            logging.info("SQL --: {}".format(sql))
            cur.execute(sql)
            relist = cur.fetchone()
        except BaseException:
            logging.error("SQL ERROR:{}".format(traceback.format_exc()))
        finally:
            cur.close()
            self.conn.close()
        return relist

    def execute(self, sql, t_index=None):
        """
        执行sql
        :param sql:
        :param t_index: transaction key (without commit)
        :return:
        """
        relist = True
        logging.info("SQL -- : {}".format(sql))
        if t_index:
            trans_cur = self.__transaction_cur[t_index]
            trans_cur.execute(sql)
        else:
            cur = self._getConnectCur()
            try:
                relist = cur.execute(sql)
                self.conn.commit()
            except BaseException:
                relist = False
                logging.error("------------------SQL ERROR: {}".format(traceback.format_exc()))
            finally:
                cur.close()
                self.conn.close()
        return relist

    def executemany(self, sql, items, t_index=None):
        """
        批量执行
        :param sql: INSERT INTO employees (name, phone) VALUES ('%s','%s')
        :param items: [ (name1, phone1), (name2, phone2) ]
        :param t_index: transaction key (without commit)
        :return:
        """
        if t_index:
            cur = self.__transaction_cur[t_index]
            cur.execute(sql, items)
        else:
            cur = self._getConnectCur()
            logging.info("SQL -- : {}".format(sql))
            try:
                cur.execute(sql, items)
                self.conn.commit()
            except BaseException:
                logging.error("SQL ERROR: {}".format(traceback.format_exc()))
            finally:
                cur.close()
                self.conn.close()
        return True

    def begin(self, t_index=None, *args, **kwargs):
        """
        transation begin
        :param t_index: 事务具柄
        :param args:
        :param kwargs:
        :return:
        """
        trans_conn = self.Pool.connection()
        if not t_index:
            t_index = str(trans_conn.__hash__())
        self.__transaction[t_index] = trans_conn
        self.__transaction_cur[t_index] = self.__transaction[t_index].cursor(cursorclass=MySQLdb.cursors.DictCursor)
        self.__transaction[t_index].begin(*args, **kwargs)
        return t_index

    def commit(self, t_index):
        """
        transaction commit
        :param t_index: 事务具柄
        :return:
        """
        trans_conn = self.__transaction[t_index]
        trans_conn.commit()

    def rollback(self, t_index):
        """
        transaction rollback
        :param t_index: 事务具柄
        :return:
        """
        trans_conn = self.__transaction[t_index]
        trans_conn.rollback()

    def close(self, t_index):
        """
        结束本次事务操作 关闭链接
        :param t_index: 事务具柄
        :return:
        """
        trans_conn = self.__transaction[t_index]
        trans_cur = self.__transaction_cur[t_index]
        trans_cur.close()
        trans_conn.close()
        self.__transaction.pop(t_index, None)
        self.__transaction_cur.pop(t_index, None)


def MultiMdbconn(mdb_configs):
    """
    多mysql库 链接池
    :param mdb_configs:
    :return:
    """
    curs_dict = {}
    for name, conf_inf in mdb_configs.items():
        curs_dict[name] = MysqlManager(conf_inf)
        print("Connection (Mysql/Maria: %s) : %s ==== successful " % (name, conf_inf))
        logging.info("Connection (Mysql/Maria: %s) : %s ==== successful " % (name, conf_inf))
    return curs_dict
