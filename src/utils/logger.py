import logging
import sys


def setup_logger(name="PicrossAutomation", level=logging.INFO):
    logger_ = logging.getLogger(name)
    logger_.setLevel(level)

    if not logger_.handlers:
        handler = logging.StreamHandler(sys.stdout)
        handler.setLevel(level)

        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%H:%M:%S'
        )
        handler.setFormatter(formatter)

        logger_.addHandler(handler)

    return logger_


logger = setup_logger()