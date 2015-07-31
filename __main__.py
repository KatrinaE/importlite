import argparse
import csv
import re
import traceback
import dbimport.table_schemas as ts
import dbimport.create_tables as ct
import dbimport.dbconn as dbconn

def read_csv(path):
    with open(path, 'rU') as data:
        reader = csv.DictReader(data)
        for row in reader:
            yield row

def create_parser():
    parser_desc = 'Create sqlite table(s) from a schema file and ' \
                  'optionally import from a CSV'
    parser = argparse.ArgumentParser(description=parser_desc)
    parser.add_argument('schema_file', metavar='schema_file', type=str,
                        help='Path to file storing table schemas')
    parser.add_argument('database', metavar='database', type=str,
                        help='Path to sqlite database')
    parser.add_argument('-f','--file', metavar='CSV FILE',
                        help='Path to CSV data to be imported'),
    parser.add_argument('-n','--no_create', action='store_true',
                        help='Do not create tables - import data only')
    return parser


if __name__ == "__main__":
    parser = create_parser()
    args = parser.parse_args()

    [conn, c] = dbconn.conn(args.database)

    create_tables = not(args.no_create)
    if create_tables == True:
        print('Creating tables...')
        try:
            ct.create_all_tables(conn, c, ts)
        except Exception as e:
            traceback.print_exc()
            exit(1)
        print("Successfully created tables")

    csv_filename = args.file
    if csv_filename is not None:
        print('Importing CSV...')
        conn.execute('BEGIN')
        for row_id, row in enumerate(read_csv(csv_filename)):
            import_row(ts, row)
        conn.execute('COMMIT')
        print('Successfully imported CSV')

    conn.close()
