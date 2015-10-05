# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import csv
import re
import sys
from importlite.schema import Table, Column


def read_csv(path):
    with open(path, 'rU') as data:
        reader = csv.DictReader(data)
        for row in reader:
            if hex(sys.hexversion) < '0x30000f0': # Python 2
                row = {unicode(col_name, "utf-8"): unicode(value, "utf-8")
	               for col_name, value in row.items()}
            yield row


def guess_schema(table_name, path):
    """Create a best-effort table schema from a CSV"""
    datatypes = tally_datatypes(enumerate(read_csv(path)))
    table = Table(table_name)

    for col_name, datatypes_tally in datatypes.items():
        most_freq_datatype = max(datatypes_tally, key=datatypes_tally.count)
        table.add_column(
            Column(col_name, most_freq_datatype)
        )
    #for col, val in table.columns.items(): print(col)
    return [table]


def tally_datatypes(csv_enumerator):
    """ Tally the most-commonly found SQLite datatype in each column of a CSV.

        For speed, only check the first 25 rows of the CSV. SQLite is
	very permissive about datatypes (see note in get_datatype) so a
	rough estimate of the most common datatype is okay.
    """
    datatypes = {}
    for data_tuple in csv_enumerator:
        if data_tuple[0] >= 25:
            break
        row = data_tuple[1]
        for col_name, value in row.items():
            datatype = get_datatype(value)
            datatypes.setdefault(col_name, []).append(datatype)
    return datatypes


def get_datatype(value):
    """ Determine most appropriate SQLite datatype for storing value.

        SQLite has only four underlying storage classes: integer, real,
        text, and blob.

        For compatibility with other flavors of SQL, it's possible to
        define columns with more specific datatypes (e.g. 'char',
        'date'), but since these are still mapped to the underlying
        storage classes there's not much point in using them when
        generating native SQLite SQL.

        Therefore, this function takes an incoming value and attempts
        to guess the best SQLite datatype for storing it. This can
        then be used to help decide the schema of the column where the
        value will be stored.

        It defaults to the text datatype, not the super-general blob
        datatype, because read_csv reads each row in as text rather
        than binary data.

        Unlike in other SQL flavors, misdefining a column's datatype
        affinity is not fatal, because in the end any type of value
        can be stored in any column. In the end, the datatype
        returned by this function is just a suggestion for SQLite.

        See:
           * https://www.sqlite.org/datatype3.html
           * http://ericsink.com/mssql_mobile/data_types.html
           * http://www.techonthenet.com/sqlite/datatypes.php
    """
    try:
        int(value)
        return 'INTEGER'
    except ValueError:
        try:
           float(value)
           return 'REAL'
        except ValueError:
            return 'TEXT'

def quote_apostrophes(value):
    """Format single quotes for SQLite.
    See:
        * http://www.sqlite.org/lang_expr.html
        * http://stackoverflow.com/questions/603572/
            how-to-properly-escape-a-single-quote-for-a-sqlite-database
    """
    return re.sub("'", "''", value)


def scrub_row(row):
    return {csv_field: quote_apostrophes(value)
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
