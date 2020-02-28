# -*- coding:utf-8 -*-
__author__ = '10029'
__time__ = '2019/12/31 10:11'
from LambdaLog import LogHandlerFactory


import logging

HOST = ""
PORT = 27017
logger = logging.getLogger(name="req")
logger.setLevel("INFO")
lh = LogHandlerFactory(
        c_name='req',
        host='127.0.0.1',
        type="Time",
        port=27017,
        backup_count=10
    )
lh.setLevel(logging.DEBUG)
formatter = logging.Formatter('[%(asctime)s] %(filename)s->%(funcName)s line:%(lineno)d [%(levelname)s]%(message)s')
lh.setFormatter(formatter)
logger.addHandler(lh)
logger.info("hello word")



