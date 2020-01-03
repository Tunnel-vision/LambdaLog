# -*- coding:utf-8 -*-
__author__ = '10029'
__time__ = '2019/12/30 20:06'
import importlib
from datetime import datetime

_datetime_factory = datetime.utcnow


class LogHandlerFactory:
    """
    创建基于mongodb的日志流 handler
    目前支持三种 handler 行为
    Standard: 日志流仅输出 mongodb数据库
    Time:     日志流输出 mongodb数据库，并基于时间做旋转
    Number:   日志流输出 mongodb数据库，并基于条数做旋转
    """

    def __new__(cls, *args, **kwargs):
        try:
            impl_cls = type(
                cls.__name__,
                (getattr(importlib.import_module('LambdaLog.impl'), kwargs.pop('type')), LogHandlerFactory),
                {}
            )
            return super(LogHandlerFactory, cls).__new__(impl_cls)
        except AttributeError:
            available_impl = getattr(importlib.import_module('LambdaLog.impl'), '__all__')
            raise ValueError(f'type of {cls.__name__} should be {", ".join(available_impl)}')

    def __init__(self, *args, **kwargs):
        raise NotImplemented

    def setLevel(self, *args, **kwargs):
        raise NotImplemented

    def setFormatter(self, *args, **kwargs):
        raise NotImplemented

    def __str__(self):
        cls_name = self.__class__.__name__
        base_cls = self.__class__.__bases__[0].__name__
        return f'<{cls_name} implemented with {base_cls}>'


if __name__ == '__main__':
    lh = LogHandlerFactory(
        c_name='new',
        host='127.0.0.1',
        type="Time",
        port=27017,
        backup_count=10
    )
    print(lh)

