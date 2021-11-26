# -*- coding: utf-8 -*-
# @Time    : 2019/08/20 下午1:54
# @Author  : Sean
# @Site    : beacon_business
# @Software: PyCharm

import logging
import logging.handlers
import logging.config

from configparser import ConfigParser
from .safeFileHandler import SafeFileHandler

# 装载配置文件
conf = ConfigParser()
conf.read("config/log.conf", encoding='utf-8')

logger = None
handler = None

logging.config.dictConfig({
    'version': 1,
    'disable_existing_loggers': False,  # 禁用未生声明的logger
    'loggers': {
        'tornado.curl_httpclient': {  # 所有的请求，打印log
            # 'handlers': LOGGING_HANDLERS, # 使用默认处理
            'level': 'INFO',
        },
        'pika': {  # mq 日志，不显示debug内容，只输出info
            # 'handlers': LOGGING_HANDLERS, # 不指定处理器， 使用默认处理
            'level': "INFO",
        },
    }
})


def initLog(file_config_field="log_file_prefix", log_to_stderr=False):
    global logger, handler

    logging.getLogger("requests").setLevel(logging.WARNING)
    logger = logging.getLogger()
    getDebug = conf.get("logs", "logging")
    # 设置日志等级-设置tornado
    logger.setLevel(getDebug.upper())
    log_file = conf.get("logs", file_config_field)
    try:
        log_step = conf.get("logs", "log_ways")
    except BaseException:
        log_step = "day"
    handler = SafeFileHandler(log_file, "a", log_step, 'utf-8')
    # 设置日志格式
    formatStr = '[%(asctime)s][%(filename)s][%(funcName)s][Line:%(lineno)d]:%(message)s'
    handler.setFormatter(logging.Formatter(formatStr))
    logger.addHandler(handler)

    if log_to_stderr:
        stream = logging.StreamHandler()
        stream.setLevel(logging.DEBUG)
        stream.setFormatter(logging.Formatter(formatStr))
        logger.addHandler(stream)
