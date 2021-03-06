# Author: Jacob Tsekrekos
# Date: Jun 21, 2018
# File: logger.py
# Description: Logging class for the engine
import logging as _logging
import os as _os

if _os.getcwd() == '__main__':
    exit(-1)

if not _os.path.exists("./logs"):
    _os.mkdir("./logs")


class Logger(_logging.Logger):
    DEBUG = 10
    INFO = 20
    WARNING = 30
    ERROR = 40
    CRITICAL = 50

    def __init__(self, name, level, log_file, format_str=None, style="{"):
        """
        :type name: str         :param name:  Specifies the name of the logger, traditionally __name__
        :type level: int        :param level: Logging enum that specifies the level of importance that will be logged
        :type log_file: str     :param log_file:  a string that holds the name of the log file
                                                  All files are stored in the project's '_logs' directory
        :type format_str: str   :param format_str: format of any messages. See logging.Formatter docs for more info
        :type style: str        :param style: format token style
        """
        super().__init__(name, level)
        log_file = _os.path.basename(log_file)
        file_handler = _logging.FileHandler("./logs/" + log_file)

        if not format_str:
            format_str = "{levelname:^8} |[{asctime}]|  {message}"
            style = "{"

        file_handler.setFormatter(_logging.Formatter(format_str, style=style))
        self.addHandler(file_handler)
