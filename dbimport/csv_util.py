import csv
import re


def read_csv(path):
    with open(path, 'rU') as data:
        reader = csv.DictReader(data)
        for row in reader:
            yield row


def remove_commas_and_apostrophes(value):
    """Remove commas and single quotes from all values in row.

    Sqlite can't handle them."""
    return re.sub("[,']", '', value)


def scrub_row(row):
    return {csv_field: remove_commas_and_apostrophes(value)
            for csv_field, value in row.items()}
