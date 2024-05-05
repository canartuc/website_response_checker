"""
This module contains functions and classes for website validation and monitoring.

The module includes the following functions:
- load_websites(file_path): Load and validate websites from a JSON file.
- is_connected(): Check if there is an internet connection.

The module also includes the following class:
- Website: A class representing a website to be monitored.
"""

import json
import re
import requests
from dataclasses import dataclass, field
from typing import List, Optional
from urllib.parse import urlparse
from logger import setup_logger, log_function_call

logger = setup_logger('validator', 'validator.log')


@dataclass
class Website:
    """
    A class representing a website to be monitored.

    Attributes:
        url (str): The URL of the website.
        interval (int): The monitoring interval in seconds.
        regex_pattern (Optional[str]): A regex pattern to match in the website content (optional).

    Raises:
        AssertionError: If the URL is not valid or the interval is not within the range of 5 to 300.
        ValueError: If the regex pattern is provided but is not a valid regex pattern.
    """

    url: str
    interval: int
    regex_pattern: Optional[str] = field(default=None)

    # Normally, __post_init__ doesn't work without __init__ but it works with dataclasses
    # because using the `@dataclass` decorator, Python automatically generates an __init__ method.
    # Validate the data after initialization. We can use this portion in tests as well, but
    # I do like to keep the validation in the class itself because in CI/CD environment, data may
    # change between the validation and the actual usage.
    def __post_init__(self):
        assert self._is_valid_url(self.url), "url must be a valid URL"
        assert isinstance(self.interval, int) and 5 <= self.interval <= 300, ("interval must be an integer between 5 "
                                                                              "and 300")
        if self.regex_pattern is not None:
            try:
                re.compile(self.regex_pattern)
            except re.error:
                raise ValueError("regex_pattern must be a valid regex pattern")

    @staticmethod
    def _is_valid_url(url: str) -> bool:
        """
        Check if a string is a valid URL.

        Args:
            url (str): The string to check.

        Returns:
            bool: True if the string is a valid URL, False otherwise.
        """
        try:
            result = urlparse(url)
            return all([result.scheme, result.netloc])
        except ValueError:
            return False


@log_function_call(logger)
def load_websites(file_path: str) -> List[Website]:
    """
    Load and validate websites from a JSON file.

    Args:
        file_path (str): The path to the JSON file.

    Returns:
        List[Website]: A list of Website objects.
    """
    with open(file_path, 'r') as file:
        websites_data = json.load(file)
    return [Website(**website) for website in websites_data]


@log_function_call(logger)
def is_connected() -> bool:
    """
    Check if there is an internet connection.

    Returns:
        bool: True if there is an internet connection, False otherwise.
    """
    try:
        requests.get('http://google.com', timeout=5)
        return True
    except requests.exceptions.RequestException:
        return False
