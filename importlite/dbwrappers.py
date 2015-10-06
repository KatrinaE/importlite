# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import sqlite3
import importlite.sqlgen as sqlgen
import importlite.csv_util as csv_util


def conn(database):
    conn = sqlite3.connect(database, 5.0, 0, None)
    conn.text_factory = str
    c = conn.cursor()
    return [conn, c]


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


def import_row_to_table(c, table, row):
    fields_to_import = [col.csv_name for col in table.columns.values()]
    row_data = {}
    for csv_field, value in sorted(row.items()):
        if csv_field in fields_to_import:
            col = csv_util.get_destination_col(table, csv_field)
            if is_foreign_key(col, table):
                value = lookup_foreign_key(c, table, col, csv_field, value)
            else:
                value = sqlgen.pre_process_value(col, value)
            row_data[col.name] = value

    if table.unique_rows == True and row_exists(c, table, row_data):
        return
    else:
        sql = sqlgen.insert_sql(table, row_data)
        c.execute(sql)


def import_row_to_all_tables(c, tables, raw_row):
    row = csv_util.scrub_row(raw_row)
    for table in tables:
        import_row_to_table(c, table, row)


def import_all_rows(conn, c, tables, rows):
    try:
        conn.execute('BEGIN')
        for row_id, row in rows:
            import_row_to_all_tables(c, tables, row)
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
    foreign_keys = query(c, foreign_key.to_table, {foreign_col_name: value})

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
        return foreign_keys[0][foreign_key.to_col]


def is_foreign_key(col, table):
    return col.name in table.foreign_keys.keys()


def get_table_schema(c, table):
    sql = sqlgen.schema_sql(table)
    table_info = c.execute(sql).fetchall()
    schema = [field[1] for field in table_info]
    return schema


def query(c, table, query_data):
    sql = sqlgen.query_sql(table, query_data)
    rows = c.execute(sql).fetchall()
    schema = get_table_schema(c, table)
    row_dicts = [dict(zip(schema, row)) for row in rows]
    return row_dicts

def row_exists(c, table, row_data):
    existing_rows = query(c, table, row_data)
    if existing_rows:
        return True
    else:
        return False
