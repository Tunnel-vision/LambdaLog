import pymongo
import logging
from logging import StreamHandler
from logging import Formatter
from LambdaLog.log import LogRecord


class LambdaStreamHandler(StreamHandler):
    """
        日志流仅输出 mongodb数据库
    """

    def __init__(self, *args, **kwargs):
        self.db_name = kwargs.get('db_name', 'lambdalog')
        self._name = kwargs.get('c_name', 'test')
        self.host = kwargs.get('host', 'localhost')
        self.port = kwargs.get('port', 27017)
        self.encoding = kwargs.get('encoding')
        self.delay = kwargs.get('delay', False)
        self.formatter = kwargs.get('formatter', Formatter())
        if self.delay:
            logging.Handler.__init__(self, *args, **kwargs)
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
        record = LogRecord.from_json(record.__dict__)
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