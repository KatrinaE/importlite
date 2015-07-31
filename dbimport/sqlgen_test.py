import unittest

import sqlgen
from table_schemas import Table, Column, ForeignKey


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

    def test_row_insert_sql(self):
        expected_sql = "INSERT INTO basic_table " \
                       "('date_field','integer_field'," \
                       "'text_field') VALUES '2010-01-01'," \
                       "'12345','hello'"
        row = {
            'csv_date_field': '2010-01-01',
            'csv_integer_field': '12345',
            'csv_text_field': 'hello'
        }
        actual_sql = sqlgen.row_insert_sql(self.basic_table, row)
        self.assertEqual(expected_sql, actual_sql)

    def test_pre_process_value(self):
        col = Column('test_col', 'TEXT', None, 'test_callback')
        processed_val = sqlgen.pre_process_value(col, 'test text')
        self.assertEqual(processed_val, 'callback succeeded')


if __name__ == '__main__':
    unittest.main()
