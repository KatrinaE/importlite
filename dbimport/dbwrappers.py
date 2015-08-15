import dbimport.dbconn as dbconn
import dbimport.sqlgen as sqlgen

def create_all_tables(conn, c, tables):
    try:
        conn.execute('BEGIN')
        for t in tables:
            dbconn.create_table(c, t)
    except:
        conn.execute('ROLLBACK')
        raise
    conn.execute('COMMIT')
        
def import_all_rows(conn, c, tables, rows):
    try:
        conn.execute('BEGIN')
        for row_id, row in rows:
            dbconn.import_row(c, tables, row)
    except:
        conn.execute('ROLLBACK')
        raise
    conn.execute('COMMIT')


class LookupForeignKeyException(Exception):
    pass

def lookup_foreign_key(c, table, foreign_key, matching_col, value):
    foreign_key = table.foreign_keys[foreign_key.from_col]
    sql = sqlgen.query_sql(foreign_key.to_table,
                           matching_col, value, foreign_key.to_col)
    foreign_key_tuples = c.execute(sql).fetchall()
    foreign_keys = [fk[0] for fk in foreign_key_tuples]

    if len(foreign_keys) == 0:
        msg = "{0} table has no row with '{1}' in the {2} column"
        raise LookupForeignKeyException(msg.format(
            foreign_key.to_table.name, value, matching_col))
    elif len(foreign_keys) > 1:
        msg = "{0} table has more than one row with {1} = '{2}'"
        raise LookupForeignKeyException(msg.format(
            foreign_key.to_table.name, matching_col, value))
    elif foreign_keys[0] == None:
        msg = "'{0}' column is empty for row where {1} == '{3}' in {3}"
        raise LookupForeignKeyException(msg.format(
            foreign_key.to_col, matching_col, value, foreign_key.to_table.name))
    else:
        return foreign_keys[0]
