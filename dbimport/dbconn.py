import sqlite3
import dbimport.sqlgen as sqlgen

def conn(database):
    conn = sqlite3.connect(database, 5.0, 0, None)
    conn.text_factory = str
    c = conn.cursor()
    return [conn, c]

def create_table(c, t):
    sql = sqlgen.create_table_sql(t)
    print(sql)
    #c.execute(sql)

def import_row(tables, row):
    row = sqlgen.remove_commas(row)
    for table in tables:
        sql = sqlgen.row_insert_sql(table, row)
        print(sql)

