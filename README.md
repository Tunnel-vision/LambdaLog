# LambdaLog

### quick start
```
import logging

from LambdaLog.handler import LogHandlerFactory
HOST = "10.1.11.143"
PORT = 27017
logger = logging.getLogger(name="req")
logger.setLevel("INFO")
lh = LogHandlerFactory(c_name=logger.name,host=HOST,type="TIME", port=PORT,backup_count=10).create_handler()
lh.setLevel(logging.DEBUG)
formatter = logging.Formatter('[%(asctime)s] %(filename)s->%(funcName)s line:%(lineno)d [%(levelname)s]%(message)s')
lh.setFormatter(formatter)
logger.addHandler(lh)
logger.info("hello word")

```

定制化的log模块，存储数据到mongo里，兼容logging模块

install step
1. python setup.py sdist
2. python setup.py install 
