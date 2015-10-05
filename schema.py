# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import re

class Table:
    """Defines a database table schema"""
    def __init__(self, name):
        self.name = name
        self.unique_rows = False
        self.columns = {}
        self.csv_col_map = {}
        self.foreign_keys = {}

    def add_columns(self, columns):
        for col in columns:
            self.add_column(col)

    def add_column(self, col):
        if not isinstance(col, Column):
            raise TypeError("col must be a Column object")
        self.columns[col.name] = col
        if col.csv_name is not None:
            self.csv_col_map[col.csv_name] = col.name

    def add_foreign_keys(self, foreign_keys):
        for fk in foreign_keys:
            self.add_foreign_key(fk)

    def add_foreign_key(self, fk):
        if not isinstance(fk, ForeignKey):
            raise TypeError("fk must be a ForeignKey object")
        self.foreign_keys[fk.from_col] = fk


class Column:
    """Defines a database column"""
    def __init__(self, name, col_type, csv_name=None, callback=None):
        """
        Arguments:
        name -- string -- column name to use in database

        col_type -- string -- a sqlite column datatype, e.g. INTEGER,
        TEXT, etc. Can also include additional keywords, such as
        PRIMARY KEY

        csv_name -- string -- (optional) column in input CSV
        containing data for this field
        """
        self.name = name
        self.col_type = col_type
        self.callback = callback

        if csv_name is not None:
            self.csv_name = csv_name
        else:
            self.csv_name = name

        self.name = re.sub("[,']", '', self.name)
        self.name = re.sub("[\s]", '_', self.name)


class ForeignKey:
    """Defines a foreign key constraint"""
    def __init__(self, from_col, to_table, to_col):
        """
        Arguments:
        from_col -- string -- name of column holding foreign key
        to_table -- Table -- Table foreign key should point to
        to_col -- string -- column foreign key should point to
        """
        self.from_col = from_col
        self.to_table = to_table
        self.to_col = to_col
