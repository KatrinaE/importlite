# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import sys
import argparse
import re
import traceback

import importlite.dbwrappers as dbwrappers
import importlite.csv_util as csv_util

def create_parser():
    parser_desc = 'Create sqlite table(s) from a schema file and ' \
                  'optionally import from a CSV'
    parser = argparse.ArgumentParser(description=parser_desc)
    parser.add_argument('database', metavar='database', type=str,
                        help='Path to sqlite database')
    parser.add_argument('-n','--no_create', action='store_true',
                        help='Do not create tables - import data only')
    parser.add_argument('-c','--csv_file', metavar='CSV FILE',
                        help='Path to CSV data to be imported')
    parser.add_argument('-s','--schema_file', metavar='SCHEMA FILE',
                        help='Path to file storing table schema')
    return parser


def load_schema_file(filename):
    """Load user-supplied schema file. Use new syntax if Python >= v3.3"""
    v = hex(sys.hexversion)
    if v >= '0x30300f0':
        import importlib.machinery
        table_schema = importlib.machinery.SourceFileLoader(
            'table_schema', filename).load_module()
    else:
        import imp
        table_schema = imp.load_source('table_schema', filename)
    return table_schema


def get_table_schema(args):
    if args.schema_file:
        table_schema = load_schema_file(args.schema_file)
        all_tables = table_schema.all_tables
    elif args.csv_file:
        all_tables = csv_util.guess_schema(args.csv_file)
    return all_tables


if __name__ == "__main__":
    parser = create_parser()
    args = parser.parse_args()

    if args.schema_file is None and args.csv_file is None:
        parser.error('CSV file and/or schema file required')

    table_definitions = get_table_schema(args)
    [conn, c] = dbwrappers.conn(args.database)

    create_tables = not(args.no_create)
    if create_tables == True:
        print('Creating tables...')
        try:
            dbwrappers.create_all_tables(conn, c, table_definitions)
        except Exception as e:
            conn.close()
            traceback.print_exc()
            exit(1)
        print("Successfully created tables")

    csv_filename = args.csv_file
    if csv_filename is not None:
        print('Importing CSV...')
        try:
            rows = enumerate(csv_util.read_csv(csv_filename))
            dbwrappers.import_all_rows(conn, c, table_definitions, rows)
        except Exception as e:
            conn.close()
            traceback.print_exc()
            exit(1)
        print('Successfully imported CSV')

    conn.close()
