"""
This module provides functions for setting up a logger with a rotating file handler
and a decorator for logging function calls.
"""

import logging
from logging.handlers import RotatingFileHandler
import os
from functools import wraps
from typing import Callable, Optional


def setup_logger(name: str, log_file: str, level: int = logging.INFO) -> logging.Logger:
    """
    Setup and return a logger with a rotating file handler.
    
    Args:
        name: The name of the logger.
        log_file: File path for the logger to write logs.
        level: Logging level, default is logging.INFO.
    
    Returns:
        Configured logger instance.
    """

    if not os.path.exists('logs'):
        os.makedirs('logs')
    logger = logging.getLogger(name)
    logger.setLevel(level)
    handler = RotatingFileHandler(f'logs/{log_file}', maxBytes=10000, backupCount=5)
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)
    if not logger.handlers:
        logger.addHandler(handler)
    return logger


def log_function_call(logger: Optional[logging.Logger] = None) -> Callable:
    """
    Decorator factory to log function calls.
    
    Args:
        logger: The logger instance to use. If None, the root logger is used.
    
    Returns:
        A decorator that logs function calls.
    """

    if logger is None:
        logger = logging.getLogger()  # Use the root logger by default

    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs) -> Callable:
            logger.info(f"Entering: {func.__name__}")
            try:
                result = func(*args, **kwargs)
                logger.info(f"Exiting: {func.__name__}")
                return result
            except Exception as e:
                logger.exception(f"Error in {func.__name__}: {e}")
                raise  # Re-raise the exception to not swallow it

        return wrapper

    return decorator
