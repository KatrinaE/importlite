# encoding: utf-8
from __future__ import unicode_literals
import sqlite3

def conn(database):
    conn = sqlite3.connect(database, 5.0, 0, None)
    conn.text_factory = str
    c = conn.cursor()
    return [conn, c]
