# -*- coding:utf-8 -*-
__author__ = '10029'
__time__ = '2019/12/30 18:01'

import json
import logging


class LogRecord(logging.LogRecord):

    def to_dict(self):
        rv = {}
        for key, value in dict.items(self.__dict__):
            rv[key] = value
        return rv

    @classmethod
    def from_json(cls, d):
        rv = object.__new__(cls)
        rv.update_from_dict(d)
        return rv

    def update_from_dict(self, d):
        self.__dict__.update(d)
        return self

    def __repr__(self):
        return json.dumps({key: value for key, value in dict.items(self.__dict__)})


if __name__ == '__main__':
    log = LogRecord.from_json(dict(
        channel="name"
    ))
    print(repr(log))
    print(log.__dict__)
