import logging
import os
from dotenv import load_dotenv


class LoggerConfig:
    """Centralized logger configuration class."""

    _instance = None
    _initialized = False

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        if not self._initialized:
            load_dotenv()
            self.LOG_LEVEL = os.getenv("LOG_LEVEL", "DEBUG").upper()
            self.LOG_FORMAT = "%(asctime)s - %(levelname)s - %(name)s - %(message)s"
            self.DATE_FORMAT = "%Y-%m-%d %H:%M:%S"
            self.LOGGER_NAME = "TT-LOGGER"
            self.VALID_LEVELS = {"DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"}

            self._initialized = True

    def get_logger(self) -> logging.Logger:
        """Configure and return a logger instance."""
        if self.LOG_LEVEL not in self.VALID_LEVELS:
            raise ValueError(f"Invalid LOG_LEVEL: {self.LOG_LEVEL}")

        logger = logging.getLogger(self.LOGGER_NAME)

        if logger.handlers:
            return logger

        logger.setLevel(self.LOG_LEVEL)

        console_handler = logging.StreamHandler()
        console_handler.setLevel(self.LOG_LEVEL)
        console_handler.setFormatter(
            logging.Formatter(self.LOG_FORMAT, datefmt=self.DATE_FORMAT)
        )
        logger.addHandler(console_handler)
        logger.propagate = False
        return logger


logger_config = LoggerConfig()

logger: logging.Logger = logger_config.get_logger()
