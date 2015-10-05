# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from __future__ import absolute_import

import unittest
import os
import sqlite3

import importlite.dbwrappers as dbwrappers
from importlite.schema import Table, Column, ForeignKey

TEST_DB = 'test_db.sqlite3'

class TestDBMethods(unittest.TestCase):

    def setUp(self):
        self.setupFixtures()
        self.setupDB()


    def setupFixtures(self):
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
        self.fk_col_a = Column('id', 'INTEGER PRIMARY KEY AUTOINCREMENT')
        self.fk_col_b = Column('basic_id', 'INTEGER')
        self.fk_col_c = Column('really_basic_id', 'INTEGER')

        self.foreign_key_table.add_columns(
            [self.fk_col_a, self.fk_col_b, self.fk_col_c])

        self.foreign_key_a = ForeignKey('basic_id', self.basic_table, 'id')
        self.foreign_key_b = ForeignKey('really_basic_id',
                                        self.really_basic_table, 'id')

        self.foreign_key_table.add_foreign_keys(
            [self.foreign_key_a, self.foreign_key_b])


    def setupDB(self):
        conn = sqlite3.connect(TEST_DB, 5.0, 0, None)
        conn.text_factory = str
        conn.execute('CREATE TABLE basic_table ' \
                     '(id INTEGER PRIMARY KEY AUTOINCREMENT, ' \
                     'date_field DATE, ' \
                     'integer_field INTEGER, ' \
                     'text_field TEXT);')

        conn.execute("INSERT INTO basic_table (text_field) " \
                     "VALUES ('foo');")
        conn.execute("INSERT INTO basic_table (text_field) " \
                     "VALUES ('bar');")
        conn.execute("INSERT INTO basic_table (text_field) " \
                     "VALUES ('bar');")

        conn.execute('CREATE TABLE foreign_key_table ' \
                     '(id INTEGER PRIMARY KEY AUTOINCREMENT, ' \
                     'basic_id INTEGER, ' \
                     'really_basic_id INTEGER);')
        self.c = conn.cursor()


    def tearDown(self):
        os.remove(TEST_DB)


    def test_lookup_foreign_key(self):
        expected_fk = 1
        actual_fk = dbwrappers.lookup_foreign_key(self.c,
                                                  self.foreign_key_table,
                                                  self.fk_col_b,
                                                  'csv_text_field',
                                                  'foo')
        self.assertEqual(expected_fk, actual_fk)


    def test_lookup_foreign_key_missing(self):
        """No row with text_field == 'baz'"""
        with self.assertRaises(dbwrappers.ForeignKeyException):
            dbwrappers.lookup_foreign_key(self.c, self.foreign_key_table,
                                          self.fk_col_b,
                                          'csv_text_field','baz')


    def test_lookup_foreign_key_duplicate(self):
        """Table has 2 rows with text_field == 'bar'"""
        with self.assertRaises(dbwrappers.ForeignKeyException):
            dbwrappers.lookup_foreign_key(self.c, self.foreign_key_table,
                                          self.fk_col_b,
                                          'csv_text_field', 'bar')


    def test_lookup_foreign_key_wrong_field(self):
        """'foo' is in text_field, not in date_field"""
        with self.assertRaises(dbwrappers.ForeignKeyException):
            dbwrappers.lookup_foreign_key(self.c, self.foreign_key_table,
                                          self.fk_col_b,
                                          'csv_date_field', 'foo')


if __name__ == '__main__':
    unittest.main()
