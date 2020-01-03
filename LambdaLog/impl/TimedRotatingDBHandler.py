from LambdaLog.impl.LambdaStreamHandler import LambdaStreamHandler


class TimedRotatingDBHandler(LambdaStreamHandler):
    """
        日志流输出 mongodb数据库，并基于时间做旋转
    """

    def __init__(self, *args, **kwargs):
        super(TimedRotatingDBHandler, self).__init__(self, *args, **kwargs)
        self.date_format = kwargs.get('date_format', '%Y-%m-%d')
        self.backup_time = kwargs.get('backup_count', 5) * 24 * 60 * 60
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
