# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import unittest
import collections

import importlite.sqlgen as sqlgen
import importlite.csv_util as csv_util
from importlite.schema import Table, Column, ForeignKey


class TestDBMethods(unittest.TestCase):

    def setUp(self):
        self.really_basic_table = Table('really_basic_table')
        self.really_basic_table.add_columns(
            [
                Column('id', 'INTEGER PRIMARY KEY AUTOINCREMENT')
            ]
        )

        self.basic_table = Table('basic_table')
        self.basic_table.add_columns(
            [
                Column('id', 'INTEGER PRIMARY KEY AUTOINCREMENT'),
                Column('date_field', 'DATE', 'csv_date_field'),
                Column('integer_field', 'INTEGER', 'csv_integer_field'),
                Column('text_field', 'TEXT', 'csv_text_field')
            ]
        )

        self.foreign_key_table = Table('foreign_key_table')
        self.foreign_key_table.add_columns(
            [
                Column('id', 'INTEGER PRIMARY KEY AUTOINCREMENT'),
                Column('basic_id', 'INTEGER'),
                Column('really_basic_id', 'INTEGER')
            ]
        )
        self.foreign_key_table.add_foreign_keys(
            [
                ForeignKey('basic_id', self.basic_table, 'id'),
                ForeignKey('really_basic_id',
                           self.really_basic_table,
                           'id')
            ]
        )

    def test_basic_create_table_sql(self):
        expected_sql = "CREATE TABLE basic_table (" \
                       "date_field DATE, " \
                       "id INTEGER PRIMARY KEY AUTOINCREMENT, " \
                       "integer_field INTEGER, " \
                       "text_field TEXT);"
        actual_sql = sqlgen.basic_create_table_sql(self.basic_table)
        self.assertEqual(expected_sql, actual_sql)


    def test_foreign_key_constraint_sql(self):
        expected_sql = "FOREIGN KEY(basic_id) " \
                       "REFERENCES basic_table(id), " \
                       "FOREIGN KEY(really_basic_id) " \
                       "REFERENCES really_basic_table(id), "
        actual_sql = sqlgen.foreign_key_constraint_sql(
            self.foreign_key_table)
        self.assertEqual(expected_sql, actual_sql)


    def test_create_table_sql(self):
        expected_sql = "CREATE TABLE foreign_key_table (" \
                       "basic_id INTEGER, " \
                       "id INTEGER PRIMARY KEY AUTOINCREMENT, " \
                       "really_basic_id INTEGER, " \
                       "FOREIGN KEY(basic_id) " \
                       "REFERENCES basic_table(id), " \
                       "FOREIGN KEY(really_basic_id) " \
                       "REFERENCES really_basic_table(id));"
        actual_sql = sqlgen.create_table_sql(self.foreign_key_table)
        self.assertEqual(expected_sql, actual_sql)

    def test_insert_sql(self):
        expected_sql = "INSERT INTO basic_table (id, date_field) " \
                       "VALUES ('12345', '2010-01-01');"
        row_data = {'id' : '12345', 'date_field' : '2010-01-01'}
        # Force dict field order so actual SQL is consistent.
        row_data = collections.OrderedDict(
            sorted(row_data.items(), reverse=True))
        actual_sql = sqlgen.insert_sql(self.basic_table, row_data)
        self.assertEqual(expected_sql, actual_sql)

    def test_query_sql(self):
        expected_sql = "SELECT * FROM basic_table WHERE 1 " \
                       "AND date_field = '2010-01-01';"
        actual_sql = sqlgen.query_sql(self.basic_table,
                                      {'date_field': '2010-01-01'})
        self.assertEqual(expected_sql, actual_sql)

    def test_query_sql_specified_cols(self):
        expected_sql = "SELECT id, integer_field FROM basic_table WHERE 1 " \
                       "AND date_field = '2010-01-01';"
        actual_sql = sqlgen.query_sql(self.basic_table,
                                      {'date_field': '2010-01-01'},
                                      ['id', 'integer_field'])
        self.assertEqual(expected_sql, actual_sql)

    def test_query_sql_multiple_parameters(self):
        expected_sql = "SELECT * FROM basic_table WHERE 1 " \
                       "AND date_field = '2010-01-01' " \
                       "AND text_field = 'foo';"
        actual_sql = sqlgen.query_sql(self.basic_table,
                                      {'date_field': '2010-01-01',
                                       'text_field': 'foo'})
        self.assertEqual(expected_sql, actual_sql)

    def test_pre_process_value(self):
        def test_callback(test_col_str):
            return 'callback succeeded'
        col = Column('test_col', 'TEXT', None, test_callback)
        processed_val = sqlgen.pre_process_value(col, 'test text')
        self.assertEqual(processed_val, 'callback succeeded')


    def test_quote_apostrophes(self):
        text = "Hello there, I've been waiting for you."
        expected_val = "Hello there, I''ve been waiting for you."
        actual_val = csv_util.quote_apostrophes(text)
        self.assertEqual(expected_val, actual_val)


if __name__ == '__main__':
    unittest.main()
