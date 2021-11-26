# -*- coding: utf-8 -*-
# @Time    : 2019/08/20 下午1:54
# @Author  : Sean
# @Site    : beacon_business
# @Software: PyCharm
import importlib
import os
import asyncio
import logging
import datetime

from tornado.platform.asyncio import AnyThreadEventLoopPolicy
from tornado import web, httpclient, httpserver, ioloop, options
from tornado.options import define, options

from config.globalConfig import DEBUG, SERVER_NAME, template_path, static_path
from tools.log import initLog

# 初始化日志
initLog(log_to_stderr=True)

# 设置最大异步请求并发量
httpclient.AsyncHTTPClient.configure(None, max_clients=1000)

# 启动参数定义
define("port", default=6910, help="options.port", type=int)
define("debug", default=DEBUG, help="options.debug", type=bool)

# 全局server
server = None


def log_request(handler):
    if handler.get_status() != 200:
        logging.error(handler.request.arguments)
    template = '[{port}][{http_code:>4}]:[{method:>4}]:[{path}]::[uid:{uid}]:[{time:0.2f}ms]:[{code}]:[{msg}]--[{arg}]'
    l_args = ':'.join(
        '{k}={v}'.format(k=key, v=value) for key, value in (getattr(handler, 'log_args', None) or {}).items())
    data = {
        'port': handler.application.port,
        'http_code': getattr(handler, 'status_code', -100),
        'time': 1000.0 * handler.request.request_time(),
        'path': handler.request.uri,
        'method': handler.request.method,
        'uid': handler.get_argument('uid', ''),
        'code': getattr(handler, 'return_code', -100),
        'msg': getattr(handler, 'return_msg', '无提示'),
        'arg': l_args
    }
    logging.error(template.format(**data))


class MyApplication(web.Application):

    def __init__(self, default_host=None, transforms=None,
                 **app_settings):
        # 收集需要使用的handlers
        service_handlers = self._import_handlers()
        self.handlers_num = len(service_handlers)
        settings = {
            "cookie_secret": "yDe94gG9Q7qttlkPujIZMR/h8MLyUUNGi1AOZ/5/qLE=",
            "cookie_config": {'expires_days': 10, 'expires': datetime.datetime.utcnow()},
            'xsrf_cookies': False,
            'debug': True if options.debug else DEBUG,
            "gzip": True,
            'log_file_prefix': os.path.join(os.path.dirname(__file__) + "/log/beacon.log"),
            'template_path': template_path,
            'static_path': static_path,
            'log_function': log_request,
        }
        """
        session_settings = dict(
            driver="redis",
            driver_settings=dict(
                host=rds_session["host"],
                port=rds_session["port"],
                db=rds_session["db"],
                max_connections=rds_session["max_conn"],
                session_cache_name=SESSION_PREFIX
            ),
            sid_name="session_id",
            session_lifetime=60 * 60 * 3
        )
        settings.update(session=session_settings)
        """
        settings.update(app_settings)
        super(MyApplication, self).__init__(service_handlers, default_host, transforms, **settings)

    @staticmethod
    def _import_handlers(handler_dir="apps"):
        """
        动态导入tornado的处理类
        :param handler_dir: handler统一归放文件夹名称
        :return:
        """
        handlers = []

        handler_path = os.path.join(os.getcwd(), handler_dir)
        if not os.path.isdir(handler_path):
            return handlers

        sub_files = next(os.walk(handler_path))[1]  # handler统一归放路径下的子文件
        for sub_file in sub_files:
            sub_file_path = os.path.join(handler_path, sub_file)  # 子文件路径

            if os.path.isdir(sub_file_path):
                for root, paths, fs in os.walk(sub_file_path):
                    if "urls.py" in fs:
                        module_li = root.split(os.sep)
                        module_name = module_li[-2] + "." + module_li[-1]
                        module = importlib.import_module(module_name + ".urls")
                        urls = getattr(module, 'urls', None)
                        if urls:
                            handlers.extend(urls)
        return handlers


def main():
    global server
    options.parse_command_line()

    # 设置全局的事件循环, 用于支持多次运行异步的事件循环
    try:
        asyncio.set_event_loop_policy(AnyThreadEventLoopPolicy())
    except BaseException:
        logging.exception("use event loop error")

    app = MyApplication()
    server = httpserver.HTTPServer(app, xheaders=True)
    server.listen(options.port, address="0.0.0.0")
    app.port = options.port
    log_words_r = "Service [%s: %s %s] start success ------ %s handlers activated" % (SERVER_NAME, options.port,
                                                                                      options.debug, app.handlers_num)
    logging.info(log_words_r)
    print(log_words_r)

    ioloop.IOLoop.instance().start()


if __name__ == '__main__':
    main()
