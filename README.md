# ImportLite: Import CSV files into SQLite databases

ImportLite is a command line utility for importing CSV files into SQLite. It can both create tables from scratch and load data into existing tables. It also offers advanced functionality, including value pre-processing and data normalization.

<!-- START doctoc generated TOC please keep comment here to allow auto update -->
<!-- DON'T EDIT THIS SECTION, INSTEAD RE-RUN doctoc TO UPDATE -->
##Table of Contents

- [ImportLite: Import CSV files into SQLite databases](#importlite-import-csv-files-into-sqlite-databases)
  - [Installation & Notes](#installation-&-notes)
  - [Prereq: Set Up Your Database](#prereq-set-up-your-database)
  - [Simple Usage](#simple-usage)
    - [Create a Table and Import Data](#create-a-table-and-import-data)
    - [Import Data to an Existing Table](#import-data-to-an-existing-table)
  - [Advanced Usage: Using Schema Files](#advanced-usage-using-schema-files)
    - [Run ImportLite with a Schema File](#run-importlite-with-a-schema-file)
    - [Specify Column Datatypes](#specify-column-datatypes)
    - [Define Additional Columns](#define-additional-columns)
    - [Change Column Names](#change-column-names)
    - [Ignore Duplicate Rows](#ignore-duplicate-rows)
    - [Pre-process Incoming Values](#pre-process-incoming-values)
    - [Normalize Incoming Data](#normalize-incoming-data)
- [Reference](#reference)
  - [Command-Line Arguments](#command-line-arguments)
  - [Schema Files](#schema-files)
    - [Columns](#columns)
    - [Tables](#tables)
    - [Foreign Keys](#foreign-keys)
- [Tests](#tests)

<!-- END doctoc generated TOC please keep comment here to allow auto update -->


## Installation & Notes

* Requires Python 2.7 or 3.2+
* Tested with SQLite v. 3.7
* Compatible with UTF-8 encoded files.


Install from the command line with pip, Python's package manager. The `--pre` flag is necessary because importlite is still at pre-release stage; the latest version is 0.1.0.

    $ pip install --pre importlite


If you don't have pip, you can also install from source:

    $ git clone https://github.com/KatrinaE/importlite importlite
    $ cd importlite
    $ python setup.py install

After installation, run ImportLite from the command line. To see options, use the `--help` switch.

    $ importlite --help

The easiest way to get started is via the examples below.

[comment]: <> (Importlite is not compatible with Python 3.0 or 3.1 because of its dependency on argparse - https://docs.python.org/3/library/argparse.html)



## Prereq: Set Up Your Database
If you haven't already, [download](https://www.sqlite.org/download.html) SQLite and create a database by following the instructions in their [introductory guide](https://www.sqlite.org/cli.html).

      cd /directory/to/put/database/in
      sqlite3 mydatabase

If you like, you can create your destination table(s) now with SQL, then skip the creation step by running `--no-create` when you run ImportLite. Otherwise, you can let ImportLite do it for you.


## Simple Usage

ImportLite can load data into both new and existing tables. Check the [reference](#command-line-arguments) section for a complete list of available options, or get started with the examples below.

### Create a Table and Import Data

To load data into a new table, use the `-c` and `-t` options:

    $ importlite -c data.csv -t newtable mydb.sqlite3

ImportLite will choose each column's datatype by inspecting the first 25 rows in the CSV. It uses the most-frequently-occurring datatype as the column's datatype. Values with different datatypes will still work because of SQLite's dynamic typing system.



### Import Data to an Existing Table

Use `-c` and `-t` with the `--no-create` argument to skip creating the sqlite table.

    $ importlite -c data.csv -t oldtable mydb.sqlite3 --no-create
    
If this option is used, any data you import will be appended to existing data. The column names in the new CSV must match the names in the SQLite table.


Note: If all you need to do is import data, you may be able to use SQLite's [bulk-loading capability](http://cs.stanford.edu/people/widom/cs145/sqlite/SQLiteLoad.html) instead of ImportLite.

## Advanced Usage: Using Schema Files

If you'd like more control over your table definitions and data handling, you can specify an advanced configuration by creating a schema file. Creating a schema file allows you to:

* Specify column names and data formats
* Define extra columns that aren't in your CSV
* Apply pre-processing functions to incoming data
* Ignore duplicate rows
* Normalize data as it's imported

Schema files are written in Python, but little Python knowledge is necessary unless you need to write a data pre-processing function. The examples below include complete schema files so you can copy, paste, and modify as needed. Save your schema file with the extension '.py' and you'll be all set.

In addition to the examples below, there is also a complete [reference](#schema-files) to the objects used in schema files.

### Run ImportLite with a Schema File
Run ImportLite with a schema file using the `-s` option:

    $ importlite -c data.csv -s schemafile.py mydb.sqlite3
    
`-s` is incompatible with `-t` (`--table-name`) because table names are defined in the schema file. However, they can be used with `-n` (`--no-create`) - this will direct ImportLite to look for existing tables that match the schema.

To create tables without importing data, use `-s` without `-c`:

    $ importlite -s schemafile.py mydb.sqlite3

### Specify Column Datatypes
If you are using a schema file, you must specify the name and type of all of the columns in your database table. 


    from importlite import Table, Column
    
    my_table = Table('mytable')
    my_table.add_columns(
        [
            Column('name', 'TEXT'),
            Column('age', 'INTEGER')
        ]
    )
    
    all_tables = (my_table)
    
Each column's name must match the name of the corresponding column in your CSV file. (skip to [Change Column Names](#change-column-names) if they do not).

The column's type (e.g. `INTEGER`) is passed through raw to SQLite, so you can use any of the SQLite datatypes. See the [official documentation](https://www.sqlite.org/datatype3.html) for more details. The discussions [here](http://ericsink.com/mssql_mobile/data_types.html) and [here](http://www.techonthenet.com/sqlite/datatypes.php) may also be helpful.


### Define Additional Columns
You can add columns to your SQLite table that aren't in your CSV by adding them to the table's schema definition. The example below creates a primary key column called `id`.

    from importlite import Table, Column
    
    my_table = Table('mytable')
    my_table.add_columns(
        [
            Column('id', 'INTEGER PRIMARY KEY AUTOINCREMENT'),
            Column('name', 'TEXT'),
            Column('age', 'INTEGER')
        ]
    )
    all_tables = (my_table)

Note: SQLite tables always have a primary key column, [ROWID](https://www.sqlite.org/lang_createtable.html#rowid), even if you do not specify a primary key in your schema. A user-defined primary key column (like the one above) is just an alias for ROWID.

### Change Column Names
If you'd like your SQLite columns to have different names than your CSV columns, you can specify a mapping when you create the column.

    from importlite import Table, Column
    
    my_table = Table('mytable')
    my_table.add_columns(
        [
            Column('sqlite_col', 'TEXT', csv_name='csv_col'),
            Column('another_col', 'INTEGER')
        ]
    )
    
    all_tables = (my_table)

In the example above, any data in `csv_col` in the CSV will be imported to `sqlite_col` in the database. The default is to assume the two names are the same, so data in `another_col` in the CSV will be imported to `another_col` in the databse.

Note: SQLite will automatically replace spaces in column names with underscores.



### Ignore Duplicate Rows
Just set the table's `unique_rows` property to True:

    from importlite import Table, Column
    
    my_table = Table('mytable')
    my_table.unique_rows = True
    my_table.add_columns(
        [
            ...
        ]
    )
    
    all_tables = (my_table)

This will ignore rows that are identical to a row already in the database.

### Pre-process Incoming Values

Heads up: you'll need to know a bit of Python to do this. 

To modify a column's values during import, pass the function to apply as a keyword argument to the column definition. Make sure to pass the function object, not it's name (so `exclaim`, not `'exclaim'`).

You can do this with both built-in functions:

    from importlite import Table, Column
    
    my_table = Table('mytable')
    my_table.add_columns(
        [
            Column('int_col', 'INTEGER', callback=int),
        ]
    )
    
    all_tables = (my_table)
    
And your own functions:

    from importlite import Table, Column
    
    def exclaim(value):
        return value + "!"
    
    my_table = Table('mytable')
    my_table.add_columns(
        [
            Column('sqlite_col', 'TEXT', 'csv_col', callback=exclaim),
        ]
    )
    
    all_tables = (my_table)
    
The first example converts each value in `int_col` to an integer before importing it. The scond example appends an exclamation point to all values in `csv_col` before saving them in `sqlite_col`.


### Normalize Incoming Data
ImportLite can normalize data as part of the import process. To perform normalization, define the tables you'd like to create in your schema file, then define the foreign key relationships between them.

You will probably want to take advantage of the `unique_rows=True` option; otherwise, your data will not be properly denormalized.

For example, say you want to denormalize the following CSV data:


    Name  | Eye Color
    ----- | ---------
    John  | Brown
    Jane  | Blue
    Joe   | Brown
    Jim   | Green


The schema file would look something like this:

    from importlite import Table, Column, ForeignKey
    
    eye_color_table = Table('eye_color')
    eye_color_table.unique_rows = True
    eye_color_table.add_columns(
        [
            Column('id', 'INTEGER PRIMARY KEY AUTOINCREMENT'),
    	    Column('eye_color', 'TEXT', csv_name='Eye Color'),
        ]
    )

    people_table = Table('people')
    people_table.add_columns(
        [
            Column('name', 'TEXT', csv_name='Name),
            Column('eye_color_id', 'TEXT', csv_name='Eye Color')
        ]
    )
    people_table.add_foreign_keys(
        [
            ForeignKey('eye_color_id', eye_color_table, 'id')
        ]
    )
    
    all_tables = (eye_color_table, people_table)

The ForeignKey in this example specifies a key from the `eye_color_id` column in `people_table` to the `id` column in `eye_color_table`. Note that the `csv_name` must be the same for both columns. (If `csv_name` isn't used, the actual column names must match).

This will create 2 tables in SQLite:

    # eye_color_table
    id | eye_color
    -- | ---------
    1  | Brown
    2  | Blue
    3  | Green

    # people_table
    name  | eye_color_id
    ----- | ------------
    John  | 1
    Jane  | 2
    Joe   | 1
    Jim   | 3


# Reference
## Command-Line Arguments
Basic usage:
  
       cd /directory/containing/importlite
       $ importlite
       
Arguments:

   * Required:
       * Path to sqlite database.
   * Optional:
       * `-h`, `--help` - print detailed help message.
       * `-c`, `--csv-file` - path to input csv file.
       * `-n`, `--no-create` - do not create tables (append data to existing ones).
      * `-s`, `--schema-file` - path to schema file. (Note: either `-s` or `-t` is required).
       * `-t`, `--table-name` - name of sqlite table to import to.


       
## Schema Files

Schema files are used for defining the final schema of your SQLite table(s). They are only required if you are pre-processing your data in some way; otherwise, you can use the script's `-t` option, which will create or find the output table automatically. See the [Advanced Usage](#advanced-usage-schema-files) section for examples of when to use schema files.

A schema file defines your tables and adds columns and foreign keys to them. There are plenty of example schema files elsewhere in this documentation, so this section simply documents the object types used in them.

### Columns
A Column contains all of the information necessary to define a column in a particular table. It holds the following information:

   * The column's SQLite name.
   * The column's SQLite datatype.
   * (Optional) The name of the CSV field to import values from (only required if the CSV name is different from the SQLite name).
   * (Optional) A callback function to apply to values before importing them.

The Column constructor is:

    Column(sqlite_name, sqlite_datatype, csv_name=foo, callback=bar)

### Tables
A Table is a container for columns and foreign keys. Its constructor is:

    Table(table_name)

Columns and foreign keys are added as follows:

    table = Table('foo')
    table.add_columns(list_of_columns)
    table.add_foreign_keys(list_of_foreign_keys)
    
If you want the table to ignore duplicate rows on input, set its `unique_rows` property to True:

    table.unique_rows = True

### Foreign Keys
A ForeignKey object defines a foreign key relationship between two columns. Before a ForeignKey can be created, all of the Tables and Columns involved must exist.

The constructor for a ForeignKey is:

    ForeignKey(from_col, to_table, to_col)    
    
# Tests
ImportLite comes with a small test suite. To run the tests:

    $ cd /directory/containing/importlite
    $ python -m unittest discover

