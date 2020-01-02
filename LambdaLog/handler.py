# -*- coding:utf-8 -*-
__author__ = '10029'
__time__ = '2019/12/30 20:06'
import logging
from logging import StreamHandler
import pymongo
from datetime import datetime
from logging import Formatter

_datetime_factory = datetime.utcnow


class LogHandlerFactory(object):
    """
        创建基于mongodb的日志流 handler
        目前支持三种 handler 行为
        STANDARD: 日志流仅输出 mongodb数据库
        TIME:     日志流输出 mongodb数据库，并基于时间做旋转
        NUMBER:   日志流输出 mongodb数据库，并基于条数做旋转
    """
    _provided_type = frozenset((
        "STANDARD", 'TIME', 'NUMBER'
    ))

    def __init__(self, db_name="lambdalog", c_name="test", host='localhost', port=27017, type=None, encoding=None,
                 backup_count=5000,
                 recycle_count=None, formatter=None, delay=False):
        self.db_name = db_name
        self._name = c_name
        self.host = host
        self.port = port
        self.encoding = encoding
        self.delay = delay
        self.type = type
        self.backup_count = backup_count
        self.recycle_count = recycle_count
        self.formatter = formatter

    def enable_provided(self, _type):
        if _type not in self._provided_type:
            return False
        return True

    def create_handler(self, **kwargs):
        if self.enable_provided(self.type):
            if self.type == "STANDARD":
                return LambdaStreamHandler(db_name=self.db_name, c_name=self._name, host=self.host, port=self.port,
                                           **kwargs)
            elif self.type == "TIME":
                return TimedRotatingDBHandler(db_name=self.db_name, c_name=self._name, host=self.host, port=self.port,
                                              backup_count=self.backup_count, **kwargs)
            elif self.type == "NUMBER":
                return NumberRotatingDBHandler(db_name=self.db_name, c_name=self._name, host=self.host, port=self.port,
                                               backup_count=self.backup_count, **kwargs)
        else:
            raise Exception("TYPE filed must be setup in [STANDARD, TIME, NUMBER]")


class LambdaStreamHandler(StreamHandler):
    """
        日志流仅输出 mongodb数据库
    """

    def __init__(self, db_name="lambdalog", c_name="test", host='localhost', port=27017, encoding=None,
                 formatter=None, delay=False):
        self.db_name = db_name
        self._name = c_name
        self.host = host
        self.port = port
        self.encoding = encoding
        self.delay = delay
        self.formatter = formatter or Formatter()
        if delay:
            logging.Handler.__init__(self)
        else:
            StreamHandler.__init__(self, self._open())

    def _open(self):
        myclient = pymongo.MongoClient("mongodb://{}:{}/".format(self.host, self.port))
        mydb = myclient[self.db_name]
        client = mydb[self.name]
        return client

    def flush(self):
        pass

    def emit(self, record):
        # self.lock.acquire()
        try:
            msg = self.format(record)
            stream = self.stream
            stream.insert_one(msg)
            self.flush()
        except Exception:
            self.handleError(record)
        # finally:
        #     self.lock.release()

    def format(self, record):
        record.message = record.getMessage()
        if self.formatter.usesTime():
            record.asctime = self.formatter.formatTime(record, self.formatter.datefmt)
        if record.exc_info:
            if not record.exc_text:
                record.exc_text = self.formatter.formatException(record.exc_info)
        record.stack_info = self.formatter.formatStack(record.stack_info)
        return record.to_dict()

    def recycle_by_conditions(self, conditions):
        stream = self.stream
        stream.delete_many(filter=conditions)

    def get_count_by_db(self):
        stream = self.stream
        return stream.find().count()

    def find_many_and_delete(self, conditions):
        stream = self.stream
        for i in range(int(conditions["count"])):
            stream.find_one_and_delete(
                {}, sort=[('created', pymongo.ASCENDING)]
            )

    def get_min_time_by_db(self):
        stream = self.stream
        return stream.find_one({}, sort=[('created', pymongo.DESCENDING)])


class TimedRotatingDBHandler(LambdaStreamHandler):
    """
        日志流输出 mongodb数据库，并基于时间做旋转
    """

    def __init__(self, db_name="lambdalog", c_name="test", host='localhost', port=27017, encoding=None, backup_count=5,
                 date_format='%Y-%m-%d', formatter=None, delay=False):
        LambdaStreamHandler.__init__(self, db_name, c_name, host, port, encoding, formatter=formatter, delay=delay)
        self.date_format = date_format
        self.backup_time = backup_count * 24 * 60 * 60
        self._timestamp = self._get_timestamp()

    def _get_timestamp(self, ):
        import time
        result = self.get_min_time_by_db()
        return result["created"] if result and "created" in result else time.time()

    def perform_rollover(self, new_timestamp):
        # 清楚 过期的
        conditions = {'created': {'$lt': new_timestamp - self.backup_time}}
        self.recycle_by_conditions(conditions=conditions)
        # 更新下 当前的时间
        self._timestamp = new_timestamp

    def emit(self, record):
        # 当前记录的时间戳 1577780231.4641
        import time
        new_timestamp = time.time()
        # 当前的时间大于 起始时间 +
        if new_timestamp >= self._timestamp + self.backup_time:
            self.perform_rollover(new_timestamp)
        super(TimedRotatingDBHandler, self).emit(record)


class NumberRotatingDBHandler(LambdaStreamHandler):
    """
        日志流输出 mongodb数据库，并基于条数做旋转
    """

    def __init__(self, db_name="lambdalog", c_name="test", host='localhost', port=27017, encoding=None,
                 backup_count=5000, recycle_count=None,
                 formatter=None, delay=False):
        self.backup_count = backup_count
        self.recycle_count = recycle_count or int(self.backup_count / 10)
        LambdaStreamHandler.__init__(self, db_name, c_name, host, port, encoding, formatter=formatter, delay=delay)

    def perform_rollover(self):
        conditions = {"count": self.recycle_count}
        self.find_many_and_delete(conditions=conditions)

    def emit(self, record):
        if self.get_count_by_db() >= self.backup_count:
            self.perform_rollover()
        super(NumberRotatingDBHandler, self).emit(record)


if __name__ == '__main__':
    myclient = pymongo.MongoClient("mongodb://:27017/")
    dblist = myclient.list_database_names()
    mydb = myclient["lambdalog"]
    mycol = mydb["req"]
    # for i in range(1):
    #     mycol.find_one_and_delete(
    #         {}, sort=[('created', pymongo.ASCENDING)]
    #     )
    # account.find().sort([("name", pymongo.ASCENDING)

    # query.remove_option()
    # mycol.find_one_and_delete({"created":{"$gt":200}},sort=[('_id', pymongo.DESCENDING)], projection={'_id': True})
    # mydict = {"name": "RUNOOB", "alexa": "10000", "url": "https://www.runoob.com"}
    # mycol.insert_one(mydict)
    # HOST = "10.1.11.143"
    # PORT = 27017
    # lh = TimedRotatingDBHandler(name="req", host=HOST, port=PORT)
    # lh.emit("haha")
