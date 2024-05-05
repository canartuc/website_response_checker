"""
This module contains a function to monitor a single URL, fetch its content, optionally check against a regex pattern,
extract matched content, and log the result along with the match (if any).

Example usage:
    monitor_url("https://example.com", r"\\d{4}-\\d{2}-\\d{2}")

"""

import requests
import time
from typing import Optional
from regex_checker import check_content_and_extract
from database import DatabaseManager
from http import HTTPStatus
from logger import log_function_call, setup_logger

monitor_logger = setup_logger('monitor_service', 'monitor_service.log')
results = []  # Store the results to the list before inserting into the database


@log_function_call(logger=monitor_logger)
def monitor_url(url: str, regex_pattern: Optional[str] = None, batch_size: int = 1000) -> None:
    """
    Monitor a single URL, fetch its content, optionally check against a regex pattern, extract matched content,
    and log the result along with the match (if any).

    Args:
        url (str): The URL to monitor.
        regex_pattern (Optional[str]): Regex pattern to check in the URL content.
        batch_size (int): The number of results to accumulate before inserting into the database.

    Raises:
        requests.exceptions.Timeout: If the request to the URL times out.
        requests.exceptions.TooManyRedirects: If there are too many redirects for the URL.
        requests.exceptions.RequestException: If the request to the URL fails.
        Exception: If an unexpected error occurs.

    """
    dbman = DatabaseManager()
    epoch_time = int(time.time())
    global results

    try:
        response = requests.get(url, timeout=10)
        response_time = response.elapsed.total_seconds()

        pattern_found, matched_content = (False, None)
        if response.status_code == HTTPStatus.OK:
            pattern_found, matched_content = check_content_and_extract(response.text, regex_pattern)

            if not pattern_found and regex_pattern:
                monitor_logger.warning(f"Pattern not found in URL {url}")

        results.append((url, float(response_time), int(response.status_code), matched_content, epoch_time, ""))

        if matched_content:
            # Handle or log the matched content as needed
            monitor_logger.info(f"Matched content in URL {url}: {matched_content}")

    except requests.exceptions.Timeout as e:
        monitor_logger.exception(f"Request timed out for {url}: {e}")
        results.append((url, float(0), int(HTTPStatus.REQUEST_TIMEOUT.value), None, epoch_time,
                        "Request timed out"))

    except requests.exceptions.TooManyRedirects as e:
        monitor_logger.exception(f"Too many redirects for {url}: {e}")
        results.append((url, float(0), int(HTTPStatus.MULTIPLE_CHOICES.value), None, epoch_time,
                        "Too many redirects"))

    except requests.exceptions.RequestException as e:
        monitor_logger.exception(f"Request failed for {url}: {e}")
        results.append((url, float(0), int(HTTPStatus.SERVICE_UNAVAILABLE.value), None, epoch_time,
                        "Request failed, service unavailable"))

    except Exception as e:
        monitor_logger.exception(f"Unexpected error for {url}: {e}")
        results.append((url, float(0), int(0), None, epoch_time, "Unexpected error"))

    # Insert results into the database if the batch size is reached
    if len(results) >= batch_size:
        dbman.stream_insert_result(results)
        results.clear()
