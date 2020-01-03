from LambdaLog.impl.LambdaStreamHandler import LambdaStreamHandler


class NumberRotatingDBHandler(LambdaStreamHandler):
    """
    日志流输出 mongodb数据库，并基于条数做旋转
    """

    def __init__(self, *args, **kwargs):
        super(NumberRotatingDBHandler, self).__init__(self, *args, **kwargs)
        self.backup_count = kwargs.get('backup_count', 5000)
        self.recycle_count = kwargs.get('recycle_count', int(self.backup_count / 10))

    def perform_rollover(self):
        conditions = {"count": self.recycle_count}
        self.find_many_and_delete(conditions=conditions)

    def emit(self, record):
        if self.get_count_by_db() >= self.backup_count:
            self.perform_rollover()
        super(NumberRotatingDBHandler, self).emit(record)
