# LambdaLog

### quick start
```
from LambdaLog import LogHandlerFactory


import logging

HOST = "10.1.11.143"
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

```

定制化的log模块，存储数据到mongo里，兼容logging模块

install step
1. python setup.py sdist
2. python setup.py install 
