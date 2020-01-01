# -*- coding:utf-8 -*-
__author__ = '10029'
__time__ = '2019/12/30 18:01'
import logging
import sys
from collections import defaultdict
from .log import LogRecord

NAMESPACE = 'lambda'
VERBOSE = 15

LEVEL_NAMES = defaultdict(lambda: logging.WARNING)  # type: Dict[str, int]
LEVEL_NAMES.update({
    'CRITICAL': logging.CRITICAL,
    'SEVERE': logging.CRITICAL,
    'ERROR': logging.ERROR,
    'WARNING': logging.WARNING,
    'INFO': logging.INFO,
    'VERBOSE': VERBOSE,
    'DEBUG': logging.DEBUG,
})

VERBOSITY_MAP = defaultdict(lambda: 0)  # type: Dict[int, int]
VERBOSITY_MAP.update({
    0: logging.INFO,
    1: VERBOSE,
    2: logging.DEBUG,
})

COLOR_MAP = defaultdict(lambda: 'blue')  # type: Dict[int, unicode]
COLOR_MAP.update({
    logging.ERROR: 'darkred',
    logging.WARNING: 'darkred',
    logging.DEBUG: 'darkgray',
})

_srcfile = logging._srcfile

class LambdaLoggerAdapter(logging.LoggerAdapter):

    @classmethod
    def getLogger(cls, name=None):
        logger = logging.getLogger(name=name)
        logger.disabled = False
        extra = dict()
        return cls(logger,extra)

    def log(self, level, msg, *args, **kwargs):  # type: ignore
        if isinstance(level, int):
            level = level
        else:
            level = LEVEL_NAMES[level]
        if self.isEnabledFor(level):
            msg, kwargs = self.process(msg, kwargs)
            self._log(level, msg, args, **kwargs)

    def _log(self, level, msg, args, exc_info=None, extra=None, stack_info=False):
        sinfo = None
        if _srcfile:
            try:
                fn, lno, func, sinfo = self.logger.findCaller(stack_info)
            except ValueError:  # pragma: no cover
                fn, lno, func = "(unknown file)", 0, "(unknown function)"
        else:  # pragma: no cover
            fn, lno, func = "(unknown file)", 0, "(unknown function)"
        if exc_info:
            if isinstance(exc_info, BaseException):
                exc_info = (type(exc_info), exc_info, exc_info.__traceback__)
            elif not isinstance(exc_info, tuple):
                exc_info = sys.exc_info()
        record = self.makeRecord(self.logger.name, level, fn, lno, msg, args,
                                 exc_info, func, extra, sinfo)
        # record.created = 50
        self.logger.handle(record)

    def verbose(self, msg, *args, **kwargs):
        self.log(VERBOSE, msg, *args, **kwargs)

    def process(self, msg, kwargs):  # type: ignore
        extra = kwargs.setdefault('extra', {})
        if 'type' in kwargs:
            extra['type'] = kwargs.pop('type')
        if 'subtype' in kwargs:
            extra['subtype'] = kwargs.pop('subtype')
        if 'location' in kwargs:
            extra['location'] = kwargs.pop('location')
        if 'nonl' in kwargs:
            extra['nonl'] = kwargs.pop('nonl')
        if 'color' in kwargs:
            extra['color'] = kwargs.pop('color')

        return msg, kwargs

    def makeRecord(self, name, level, fn, lno, msg, args, exc_info,
                   func=None, extra=None, sinfo=None):
        """
        A factory method which can be overridden in subclasses to create
        specialized LogRecords.
        """
        rv = LogRecord(name, level, fn, lno, msg, args, exc_info, func,
                               sinfo)
        if extra is not None:
            for key in extra:
                if (key in ["message", "asctime"]) or (key in rv.__dict__):
                    raise KeyError("Attempt to overwrite %r in LogRecord" % key)
                rv.__dict__[key] = extra[key]
        return rv

    def addHandler(self, hdlr):
        self.logger.addHandler(hdlr)

    def removeHandler(self, hdlr):
        self.logger.removeHandler(hdlr)
