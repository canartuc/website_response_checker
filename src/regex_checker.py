"""
A module for checking content against a regex pattern and extracting the matched content.

This module provides a function `check_content_and_extract` that takes a text content and a regex pattern as input.
It checks if the given regex pattern is found in the content and extracts the matched content.

Example usage:
    content = "Hello, world!"
    pattern = r"Hello"
    result = check_content_and_extract(content, pattern)
    print(result)  # (True, "Hello")
"""

import re
from typing import Optional, Tuple


def check_content_and_extract(content: str, pattern: Optional[str]) -> Tuple[bool, Optional[str]]:
    """
    Check if the given regex pattern is found in the content and extract the matched content.

    Args:
        content: The text content to search within.
        pattern: The regex pattern to search for. If None, the function considers the check passed without searching.

    Returns:
        A tuple where the first element indicates whether the pattern was found (bool),
        and the second element is the matched content (str) or None if there was no match or no pattern provided.
    """

    if pattern is None:
        return True, None

    match = re.search(pattern, content)
    if match:
        # Returns the entire match
        return True, match.group(0)

    return False, None
