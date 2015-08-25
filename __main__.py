import argparse
import re
import traceback
import importlib.machinery

import importlite.dbwrappers as dbwrappers
import importlite.dbconn as dbconn
import importlite.csv_util as csv_util

def create_parser():
    parser_desc = 'Create sqlite table(s) from a schema file and ' \
                  'optionally import from a CSV'
    parser = argparse.ArgumentParser(description=parser_desc)
    parser.add_argument('database', metavar='database', type=str,
                        help='Path to sqlite database')
    parser.add_argument('-n','--no_create', action='store_true',
                        help='Do not create tables - import data only')
    parser.add_argument('-f','--file', metavar='CSV FILE',
                        help='Path to CSV data to be imported')
    parser.add_argument('-s','--schema_file', metavar='SCHEMA FILE',
                        help='Path to file storing table schema')
    return parser


def get_table_schema(args):
    if args.schema_file:
        table_schema = importlib.machinery.SourceFileLoader(
            'table_schema', args.schema_file).load_module()
        all_tables = table_schema.all_tables
    elif args.file:
        print('creating table from file')
        all_tables = csv_util.guess_schema(args.file)
    return all_tables


if __name__ == "__main__":
    parser = create_parser()
    args = parser.parse_args()

    if args.schema_file is None and args.file is None:
        parser.error('CSV file and/or schema file required')

    table_definitions = get_table_schema(args)
    [conn, c] = dbconn.conn(args.database)

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

    csv_filename = args.file
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
