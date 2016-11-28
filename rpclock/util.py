import logging
import sys


def setup_logging(name):
    fmt = '%(name)s - %(levelname)s - %(message)s'

    std_handler = logging.StreamHandler(sys.stdout)
    std_handler.setFormatter(logging.Formatter(fmt))

    logger = logging.getLogger(name)
    logger.addHandler(std_handler)
    logger.setLevel(logging.DEBUG)
    logger.propagate = False