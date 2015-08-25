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


def get_destination_col(table, csv_field):
    destination_cols = [col for col in table.columns.values()
                        if col.csv_name == csv_field]
    if len(destination_cols) > 1:
        raise Exception('Expected one column in {0} to import data from ' \
                        'csv field {1}; more than one found.'
                        .format(table.name, csv_field))
    elif len(destination_cols) < 1:
        raise Exception('Expected one column in {0} to import data from ' \
                        'csv field {1}; none found.'
                        .format(table.name, csv_field))
    else:
        return destination_cols[0]
