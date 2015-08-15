import re

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


def db_col_format(values):
    return "{0}".format(", ".join(values))


def db_val_format(values):
    return "'{0}'".format("', '".join(values))


def insert_sql(table, row_data):
    col_str = db_col_format(row_data.keys())
    val_str = db_val_format(row_data.values())
    sql = "INSERT INTO {0} ({1}) VALUES {2};"
    sql = sql.format(table.name, col_str, val_str)
    return sql


def query_sql(table, col_name, value, return_cols='*'):
    if isinstance(return_cols, str):
        return_cols = [return_cols]
    return_col_str = db_col_format(return_cols)
    sql = "SELECT {0} FROM {1} WHERE {2} = '{3}';"
    sql = sql.format(return_col_str, table, col_name, value)
    return sql


def remove_commas(row):
    """Remove commas from values because sqlite can't handle them"""
    for field, value in row.items():
        row[field] = re.sub(',', '', value)
    return row


def pre_process_value(col, value):
    """Strip whitespace and optionally apply a callback func"""
    if col.callback is not None:
        value = col.callback(value)
    return value.strip()


def row_insert_sql(table, row):
    """Return the SQL to add the given row to the given table"""
    columns = []
    values = []
    for csv_field, value in sorted(row.items()):
        if csv_field in table.csv_col_map:
            col_name = table.csv_col_map[csv_field]
            col = table.columns[col_name]
            columns.append(col_name)

            value = pre_process_value(col, value)
            values.append(value)

    col_str = db_col_format(columns)
    val_str = db_val_format(values)
    sql = "INSERT INTO {0} ({1}) VALUES {2};"
    sql = sql.format(table.name, col_str, val_str)
    print(sql)
    return sql
