#!/usr/bin/env python3
"""
This module monitors a list of websites continuously using multiple threads.
"""

import time
import threading
from datetime import datetime
from typing import List, Generator
import multiprocessing
from monitor_service import monitor_url
from logger import log_function_call, setup_logger
from validator import is_connected, load_websites, Website

main_logger = setup_logger('main', 'main.log')


@log_function_call(logger=main_logger)
def chunk_websites(website_list: List[Website], chunk_size: int) -> Generator[List[Website], None, None]:
    """
    Split the list of websites into smaller chunks.

    Args:
        website_list: A list of Website objects.
        chunk_size: The size of each chunk.

    Yields:
        A chunk of websites as a list.
    """
    for i in range(0, len(website_list), chunk_size):
        yield website_list[i:i + chunk_size]


def monitor_website_continuous(website: Website):
    """
    Monitor a single website continuously at specified intervals.

    Args:
        website: The Website object to monitor.
    """
    while True:
        if not is_connected():
            main_logger.error("(!!!) No internet connection.")
            continue
        print(f"({datetime.now()}) Monitoring: {website.url}")
        monitor_url(website.url, website.regex_pattern)
        time.sleep(website.interval)


@log_function_call(logger=main_logger)
def monitor_websites_chunk(websites_chunk: List[Website]) -> None:
    """
    Monitor a chunk of websites using separate threads.

    Args:
        websites_chunk: A chunk of websites as a list.
    """
    for website in websites_chunk:
        threading.Thread(target=monitor_website_continuous, args=(website,)).start()


if __name__ == "__main__":
    websites_data = load_websites('websites.json')
    websites = [Website(data.url, data.interval, data.regex_pattern) for data in websites_data]
    num_cores = multiprocessing.cpu_count()
    websites_per_chunk = max(1, len(websites) // num_cores)

    for chunk in chunk_websites(websites, websites_per_chunk):
        threading.Thread(target=monitor_websites_chunk, args=(list(chunk),)).start()
