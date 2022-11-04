import logging

_log_format = '%(asctime)s - [%(levelname)s] - %(name)s - (%(filename)s).%(funcName)s(%(lineno)d) - %(message)s'


def get_file_errors_handler() -> logging.Handler:
    """Creates and configures the error handler that will record messages about their
     detection in a special log file (errors)

     :return: errors handler
     :rtype: Handler

     """
    file_handler = logging.FileHandler(filename="./tg_bot/services/logger/errors.log",
                                       encoding='utf-8')
    file_handler.setLevel(logging.ERROR)
    file_handler.setFormatter(logging.Formatter(_log_format))
    return file_handler


def get_file_journal_handler() -> logging.Handler:
    """Creates and configures the handler that will record messages about all user activity
    in a special log file (journal)

    :return:  info handler (severity of logger's messages below error level)
    :rtype: Handler

    """
    file_handler = logging.FileHandler(filename="./tg_bot/services/logger/journal.log",
                                       encoding='utf-8')
    file_handler.setLevel(logging.INFO)
    file_handler.setFormatter(logging.Formatter(_log_format))
    return file_handler


def get_stream_handler() -> logging.Handler:
    """Creates and configures the handler that will show messages about all user activity
    in a progamm console, without recording to the special log file

    :return:  info handler (severity of logger's messages - DEBUG level)
    :rtype: Handler

    """
    stream_handler = logging.StreamHandler()
    stream_handler.setLevel(logging.DEBUG)
    stream_handler.setFormatter(logging.Formatter(_log_format))
    return stream_handler


def get_logger(name: str) -> logging.Logger:
    """Creates and configures the logger object, accepts the necessary handlers

    :param: name: name of current module:
    :type: name: string
    :return: current logger
    :rtype: Logger

    """
    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)
    logger.addHandler(get_file_errors_handler())
    logger.addHandler(get_file_journal_handler())
    logger.addHandler(get_stream_handler())
    return logger
