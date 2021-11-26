# -*- coding: utf-8 -*-
# @Time    : 2019/08/20 下午1:54
# @Author  : Sean
# @Site    : beacon_business
# @Software: PyCharm


import time
from logging import FileHandler

s__all__ = [
    "BASIC_FORMAT", "BufferingFormatter", "CRITICAL", "DEBUG", "ERROR", "FATAL",
    "FileHandler", "Filter", "Formatter", "Handler", "INFO", "LogRecord", "Logger",
    "LoggerAdapter", "NOTSET", "NullHandler", "StreamHandler", "WARN", "WARNING",
    "addLevelName", "basicConfig", "captureWarnings", "critical", "debug", "disable",
    "error", "exception", "fatal", "getLevelName", "getLogger", "getLoggerClass", "info",
    "log", "makeLogRecord", "setLoggerClass", "warn", "warning"
]

try:
    import codecs
except ImportError:
    codecs = None

try:
    import thread
    import threading
except ImportError:
    thread = None


class SafeFileHandler(FileHandler):
    def __init__(self, filename, mode, ways="day", encoding=None, delay=0):
        """
        Use the specified filename for streamed logging
        """
        if codecs is None:
            encoding = None
        FileHandler.__init__(self, filename, mode, encoding, delay)
        self.mode = mode
        self.encoding = encoding
        # self.suffix = "%Y%m%d"
        self.setSuffix(ways)
        self.suffix_time = ""

    # ----------------------------------------------------------------------
    def setSuffix(self, ways):
        """
        设置日志分割方式：月，天，小时
        """
        if ways == "month":
            self.suffix = "%Y%m"
        elif ways == "hour":
            self.suffix = "%Y%m%d%H"
        else:
            self.suffix = "%Y%m%d"

    def emit(self, record):
        """
        Emit a record.

        Always check time
        """
        try:
            if self.check_baseFilename(record):
                self.build_baseFilename()
            FileHandler.emit(self, record)
        except (KeyboardInterrupt, SystemExit):
            raise
        except BaseException:
            self.handleError(record)

    def check_baseFilename(self, record):
        """
        Determine if builder should occur.

        record is not used, as we are just comparing times,
        but it is needed so the method signatures are the same
        """
        timeTuple = time.localtime()

        if self.suffix_time != time.strftime(self.suffix, timeTuple) or not self.baseFilename.endswith(
                time.strftime(self.suffix, timeTuple)):
            return 1
        else:
            return 0

    def build_baseFilename(self):
        """
        do builder; in this case,
        old time stamp is removed from filename and
        a new time stamp is append to the filename
        """
        if self.stream:
            self.stream.close()
            self.stream = None

        # remove old suffix
        if self.suffix_time != "":
            index = self.baseFilename.find("." + self.suffix_time)
            if index == -1:
                index = self.baseFilename.rfind(".")
            self.baseFilename = self.baseFilename[:index]

        # add new suffix
        currentTimeTuple = time.localtime()
        self.suffix_time = time.strftime(self.suffix, currentTimeTuple)
        self.baseFilename = self.baseFilename + "." + self.suffix_time

        self.mode = 'a'
        if not self.delay:
            self.stream = self._open()
