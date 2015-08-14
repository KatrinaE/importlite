import dbimport.sqlgen as sqlgen

def create_table(c, t):
    sql = sqlgen.create_table_sql(t)
    print(sql)
    #c.execute(sql)

def create_all_tables(conn, c, tables):
    try:
        conn.execute('BEGIN')
        for t in tables:
            create_table(c, t)
    except:
        conn.execute('ROLLBACK')
        raise
    conn.execute('COMMIT')
        
def import_row(tables, row):
    row = sqlgen.remove_commas(row)
    for table in tables:
        sql = sqlgen.row_insert_sql(table, row)
        print(sql)

def import_all_rows(conn, tables, rows):
    try:
        conn.execute('BEGIN')
        for row_id, row in rows:
            import_row(tables, row)
    except:
        conn.execute('ROLLBACK')
        raise
    conn.execute('COMMIT')


def lookup_foreign_key(c, table, col_name, value):
    foreign_table = foreign_key.table
    foreign_col = table.foreign_keys[col_name]
    sql = sqlgen.query_sql(foreign_table.name, foreign_col.name, value, 'id')
    foreign_ids = c.execute(sql)

    if len(foreign_ids) == 0:
        msg = "{0} table has no entry '{1}' in the {2} column"
        raise Exception(msg.format(foreign_table.name, row[csv_col], col_name))
    elif len(foreign_ids) > 1:
        msg = "{0} table has more than one row with {1} = {2}"
        raise Exception(msg.format(foreign_table.name, col_name, row[csv_col]))
    else:
        return foreign_keys[0]
