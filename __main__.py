import argparse
import re
import traceback
import importlib.machinery
import dbimport.dbwrappers as dbwrappers
import dbimport.dbconn as dbconn
import dbimport.csv_util as csv_util

def create_parser():
    parser_desc = 'Create sqlite table(s) from a schema file and ' \
                  'optionally import from a CSV'
    parser = argparse.ArgumentParser(description=parser_desc)
    parser.add_argument('schema_file', metavar='schema_file', type=str,
                        help='Path to file storing table schemas')
    parser.add_argument('database', metavar='database', type=str,
                        help='Path to sqlite database')
    parser.add_argument('-n','--no_create', action='store_true',
                        help='Do not create tables - import data only')
    parser.add_argument('-f','--file', metavar='CSV FILE',
                        help='Path to CSV data to be imported'),
    return parser


if __name__ == "__main__":
    parser = create_parser()
    args = parser.parse_args()
    print(args)

    [conn, c] = dbconn.conn(args.database)

    table_schema = importlib.machinery.SourceFileLoader(
       'table_schema', args.schema_file).load_module()

    create_tables = not(args.no_create)
    if create_tables == True:
        print('Creating tables...')
        try:
            dbwrappers.create_all_tables(conn, c, table_schema.all_tables)
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
            dbwrappers.import_all_rows(conn, c, table_schema.all_tables, rows)
        except Exception as e:
            conn.close()
            traceback.print_exc()
            exit(1)
        print('Successfully imported CSV')

    conn.close()
