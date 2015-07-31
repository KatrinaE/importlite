import dbimport.sqlgen as sqlgen

def create_table(c, t):
    sql = sqlgen.create_table_sql(t)
    print(sql)
    #c.execute(sql)

def create_all_tables(conn, c, ts):
    try:
        conn.execute('BEGIN')
        for t in ts.all_tables:
            create_table(c, t)
    except:
        conn.execute('ROLLBACK')
        conn.close()
        raise
    conn.execute('COMMIT')
        
def import_row(ts, row):
    row = sqlgen.remove_commas(row)
    for table in ts.all_tables:
        sql = sqlgen.row_insert_sql(table, row)
        print(sql)
