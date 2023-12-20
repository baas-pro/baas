import logging
import os
import sys
from datetime import datetime

from common import config, app


class ColoredHTMLFormatter(logging.Formatter):
    """
    Formatter that adds HTML color tags depending on the log level.
    """
    COLORS = {
        'DEBUG': 'blue',
        'INFO': 'green',
        'WARNING': 'orange',
        'ERROR': 'red',
        'CRITICAL': 'purple'
    }

    DATE_COLOR = 'blue'

    def format(self, record):
        level_color = self.COLORS.get(record.levelname, 'black')
        record.asctime = self.formatTime(record, "%H:%M:%S")

        # 保证levelname至少10个字符长，不足的话用&nbsp;补齐
        padded_levelname = record.levelname.ljust(9).replace(' ', '&nbsp;')
        record.levelname = f'<span style="color:gray">{app.version}</span>&nbsp;&nbsp;<span style="color: {level_color};">{padded_levelname}</span>'

        message = super().format(record)
        return message.replace('\n', '<br />')

    # Override formatTime to use our custom date format
    def formatTime(self, record, datefmt=None):
        datefmt = "%m-%d %H:%M:%S"
        ct = datetime.fromtimestamp(record.created)
        if datefmt:
            s = ct.strftime(datefmt)
        else:
            try:
                s = ct.isoformat(timespec='milliseconds')
            except TypeError:
                s = ct.isoformat()
        return s


class StreamToLogger:
    """
    Fake file-like stream object that redirects writes to a logger instance.
    """

    def __init__(self, logger, level):
        self.logger = logger
        self.level = level

    def write(self, message):
        if message.rstrip() != "":
            self.logger.log(self.level, message.rstrip())

    def flush(self):
        pass


def pad_string(s):
    length = len(s)
    if length < 10:
        s += '&nbsp;' * (10 - length)
    return s


def create_logger(con, html_logger=True):
    logger = logging.getLogger('my_logger')
    logger.setLevel(logging.DEBUG)
    if html_logger and not logger.handlers:
        log_dir_path = config.resource_path('runtime/logs')
        if not os.path.exists(log_dir_path):
            os.makedirs(log_dir_path)
            print(f"The directory {log_dir_path} was created.")
        current_date = datetime.now().strftime('%Y-%m-%d')
        log_path = config.resource_path(f'runtime/logs/{current_date}_{con}.html')
        file_handler = logging.FileHandler(log_path, encoding='utf-8')
        file_handler.setLevel(logging.DEBUG)

        formatter = ColoredHTMLFormatter(
            '<p>%(levelname)s<span style="color:#0598bc">%(asctime)s</span> │ <span style="color:#616161">%(message)s</span></p>')
        file_handler.setFormatter(formatter)

        logger.addHandler(file_handler)

        stdout_logger_handler = StreamToLogger(logger, logging.INFO)
        stderr_logger_handler = StreamToLogger(logger, logging.ERROR)

        sys.stdout = stdout_logger_handler
        sys.stderr = stderr_logger_handler
        logger.info(title("日志初始化成功"))
    return logger


def title(msg):
    pre = '</br>'
    s = '<span style="color: #14ce14; text-decoration-color: #14ce14">═════════════════════════════════════════════════════════════════════════════════════════════════</span>'
    return pre + s + "</br><div style='color:#42A5F5;width:800px;' align='center'>" + msg + "</div>" + s
