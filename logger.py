import logging

ROOT_NAME = 'smc'


def setup(level=logging.INFO):
    logger = logging.getLogger(ROOT_NAME)
    logger.setLevel(level)

    formatter = logging.Formatter(
        '[%(asctime)s %(levelname)s %(filename)s:%(lineno)d] %(message)s')
    handler = logging.StreamHandler()
    handler.setFormatter(formatter)
    logger.addHandler(handler)


def get(name):
    return logging.getLogger(
        '{}.{}'.format(ROOT_NAME, name))
