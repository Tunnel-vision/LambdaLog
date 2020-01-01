# -*- coding:utf-8 -*-
__author__ = '10029'
__time__ = '2019/12/31 10:11'


from LambdaLog import LambdaLoggerAdapter
import logging

from LambdaLog.handler import NumberRotatingDBHandler

HOST = "10.1.11.143"
PORT = 27017
logger = LambdaLoggerAdapter.getLogger(name="req")
logger.setLevel("INFO")
# lh = LambdaStreamHandler(name=logger.logger.name,host=HOST, port=PORT)
# lh = TimedRotatingDBHandler(name=logger.logger.name,host=HOST, port=PORT)
lh = NumberRotatingDBHandler(name=logger.logger.name,host=HOST, port=PORT,backup_count=10)
lh.setLevel(logging.DEBUG)
formatter = logging.Formatter('[%(asctime)s] %(filename)s->%(funcName)s line:%(lineno)d [%(levelname)s]%(message)s')
lh.setFormatter(formatter)
logger.addHandler(lh)
logger.info("hello word")



