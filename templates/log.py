## Logger configuration
## Change level by changing DEBUG_LEVEL variable to ["DEBUG", "INFO", "WARNING", "ERROR"]
import logging, sys 

DEBUG_LEVEL = "INFO"
LOGGER_HANDLER=sys.stdout
LOGGER_FORMAT = '[%(filename)s:%(lineno)d] %(levelname)s:  %(message)s'


def log(name, level = DEBUG_LEVEL, handler = LOGGER_HANDLER, format = LOGGER_FORMAT, ):
    logger = logging.getLogger(name)
    logger.setLevel(logging.getLevelName(level))

    handler = logging.StreamHandler(handler)
    handler.setLevel(logging.getLevelName(level))
    format = logging.Formatter(format)
    handler.setFormatter(format)
    logger.addHandler(handler)
    return logger