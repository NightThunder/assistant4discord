import logging
from pathlib import Path


def setup_logger(name=__name__, log_name='new.log', level=logging.DEBUG, format='%(asctime)s: %(levelname)s: %(message)s'):

    log_file = str(Path(__file__).parents[1]) + '/data/' + log_name

    logger = logging.getLogger(name)
    logger.setLevel(level)

    formatter = logging.Formatter(format)

    file_handler = logging.FileHandler(log_file)
    file_handler.setFormatter(formatter)

    logger.addHandler(file_handler)

    return logger
