from datetime import datetime
import logging
import sys
import time
import os


class Formatter(logging.Formatter):
    def formatTime(self, record, datefmt=None):
        milliseconds = int(record.msecs)
        formatted_time = (
            time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(record.created))
            + f".{milliseconds:03.0f}"
        )
        return formatted_time


class Logger(logging.Logger):
    def __init__(self, name: str, log_file: str = None, level: int = logging.INFO):
        """
        Initialize the CustomLogger class.

        Parameters:
        - name: str, the name of the logger
        - log_file: str, optional, path to the log file (if not provided, logs will be printed to the console)
        - level: int, the logging level (default is logging.INFO)
        """
        super().__init__(name, level)
        self.setLevel(level)
        formatter = Formatter(
            "[%(asctime)s] [%(levelname)s] [%(filename)s:%(funcName)s:%(lineno)s] %(message)s"
        )
        # Create handlers
        if log_file:
            # Generate log file name with datetime
            file_handler = logging.FileHandler(log_file)
            file_handler.setFormatter(formatter)
            file_handler.setLevel(level)
            self.addHandler(file_handler)

        # Console handler
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setFormatter(formatter)
        console_handler.setLevel(level)
        self.addHandler(console_handler)

        # Ensure the logger doesn't propagate to parent loggers
        self.propagate = False

if not os.path.exists("./logs"):
    os.makedirs("./logs")
log_file_path = f"./logs/trading_{datetime.now().strftime('%Y-%m-%d')}.log"
logger = Logger("trading", log_file=log_file_path, level=logging.INFO)
