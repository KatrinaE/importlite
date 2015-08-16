import dbimport.sqlgen as sqlgen
import dbimport.csv_util as csv_util


def create_table(c, table):
    sql = sqlgen.create_table_sql(table)
    c.execute(sql)


def create_all_tables(conn, c, tables):
    try:
        conn.execute('BEGIN')
        for t in tables:
            create_table(c, t)
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


class ForeignKeyException(Exception):
    pass

def lookup_foreign_key(c, table, col, csv_field, value):
    foreign_key = table.foreign_keys[col.name]
    matching_foreign_col = csv_util.get_destination_col(foreign_key.to_table,
                                                        csv_field)
    value = sqlgen.pre_process_value(matching_foreign_col, value)
    foreign_col_name = matching_foreign_col.name
    sql = sqlgen.query_sql(foreign_key.to_table, foreign_col_name,
                           value, foreign_key.to_col)
    foreign_key_tuples = c.execute(sql).fetchall()
    foreign_keys = [fk[0] for fk in foreign_key_tuples]

    if len(foreign_keys) == 0:
        msg = "{0} table has no row with '{1}' in the {2} column"
        raise ForeignKeyException(msg.format(
            foreign_key.to_table.name, value, foreign_col_name))
    elif len(foreign_keys) > 1:
        msg = "{0} table has more than one row with {1} = '{2}'"
        raise ForeignKeyException(msg.format(
            foreign_key.to_table.name, foreign_col_name, value))
    elif foreign_keys[0] == None:
        msg = "'{0}' column is empty for row where {1} == '{3}' in {3}"
        raise ForeignKeyException(msg.format(
            foreign_key.to_col, foreign_col_name, value,
            foreign_key.to_table.name))
    else:
        return foreign_keys[0]


def is_foreign_key(col, table):
    return col.name in table.foreign_keys.keys()
