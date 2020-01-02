# -*- coding:utf-8 -*-
__author__ = '10029'
__time__ = '2019/12/31 10:11'


from LambdaLog import LambdaLoggerAdapter
import logging

from LambdaLog.handler import LogHandlerFactory

HOST = "10.1.11.143"
PORT = 27017
logger = LambdaLoggerAdapter.getLogger(name="req")
logger.setLevel("INFO")
lh = LogHandlerFactory(c_name=logger.logger.name,host=HOST,type="TIME", port=PORT,backup_count=10).create_handler()
lh.setLevel(logging.DEBUG)
formatter = logging.Formatter('[%(asctime)s] %(filename)s->%(funcName)s line:%(lineno)d [%(levelname)s]%(message)s')
lh.setFormatter(formatter)
logger.addHandler(lh)
logger.info("hello word")



