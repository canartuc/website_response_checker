#!/usr/bin/env python

import csv
import json
import random

"""
This script reads a CSV file containing website URLs
(https://gist.githubusercontent.com/bejaneps/ba8d8eed85b0c289a05c750b3d825f61/raw/6827168570520ded27c102730e442f35fb4b6a6d/websites.csv)
and for each website, generates a random interval between 5 and 300 seconds. It then writes the data to a JSON file.
"""


def process_row(row):
    return {
        "url": "https://" + str(row[1]).strip().replace('"', ''),
        "interval": random.randint(5, 300),  # Random interval
        "regex_pattern": None
    }


with open('websites.csv', 'r') as file:
    reader = csv.reader(file)
    websites = [process_row(row) for row in reader]

with open('../websites.json', 'w') as outfile:
    json.dump(websites, outfile, indent=4)
