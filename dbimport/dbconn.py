import sqlite3
import dbimport.sqlgen as sqlgen

def conn(database):
    conn = sqlite3.connect(database, 5.0, 0, None)
    conn.text_factory = str
    c = conn.cursor()
    return [conn, c]


def import_row(c, tables, row):
    row = sqlgen.remove_commas(row)
    for table in tables:
        sql = sqlgen.row_insert_sql(table, row)
        print(sql)
        #c.execute(sql)
