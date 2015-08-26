# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import re
import sys

def create_table_sql(table):
    """Return all SQL to create a table, incl foreign key constraints"""
    create_sql = basic_create_table_sql(table)
    foreign_key_sql = foreign_key_constraint_sql(table)

    create_sql = re.sub('\);$', ', ', create_sql)
    sql = create_sql + foreign_key_sql
    sql = re.sub(', $', '', sql) + ");"
    return sql


def basic_create_table_sql(table):
    """Return the SQL to create a table from the given schema.

    Does not include foreign keys or other constraints, only the SQL
    to make columns of the given name/type combinations.
    """
    sql = "CREATE TABLE {name} (".format(name=table.name)
    col_names = list(table.columns.keys())
    for col_name in sorted(col_names):
        col = table.columns[col_name]
        sql += "{fn} {ff}, ".format(fn=col.name, ff=col.col_type)
    sql = re.sub(', $', '', sql) + ");"
    return sql


def foreign_key_constraint_sql(table):
    """Return the SQL to add foreign key constraints to a given table"""
    sql = ''
    fk_names = list(table.foreign_keys.keys())
    for fk_name in sorted(fk_names):
        foreign_key = table.foreign_keys[fk_name]
        sql += "FOREIGN KEY({fn}) REFERENCES {tn}({kc}), ".format(
            fn=foreign_key.from_col,
            tn=foreign_key.to_table.name,
            kc=foreign_key.to_col
        )
    return sql


def db_col_format(col_names):
    return "{0}".format(", ".join(col_names))


def db_val_format(values):
    if hex(sys.hexversion) < '0x30000f0': # Python 2
        str_values = [unicode(val) for val in values]
    else:
        str_values = [str(val) for val in values]
    return "'{0}'".format("', '".join(str_values))


def insert_sql(table, row_data):
    col_str = db_col_format(row_data.keys())
    val_str = db_val_format(row_data.values())
    sql = "INSERT INTO {0} ({1}) VALUES ({2});"
    sql = sql.format(table.name, col_str, val_str)
    return sql


def query_sql(table, query_data, return_cols='*'):
    if isinstance(return_cols, str):
        return_cols = [return_cols]
    return_col_str = db_col_format(return_cols)
    sql = "SELECT {0} FROM {1} WHERE 1".format(return_col_str, table.name)
    for col_name, value in sorted(query_data.items()):
        sql += " AND {0} = '{1}'".format(col_name, value)
    sql += ";"
    return sql


def schema_sql(table):
    return 'PRAGMA TABLE_INFO({});'.format(table.name)


def pre_process_value(col, value):
    """Strip whitespace and optionally apply a callback func"""
    if col.callback is not None:
        value = col.callback(value)
    return value.strip()
