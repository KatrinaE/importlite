class Table:
    """Defines a database table schema"""
    def __init__(self, name):
        self.name = name
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
        self.csv_name = csv_name
        self.callback = callback


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


restaurant_table = Table('r_restaurant')
restaurant_table.add_columns(
    [
        Column('id', 'INTEGER PRIMARY KEY AUTOINCREMENT'),
        Column('building', 'TEXT', 'BUILDING'),
        Column('street', 'TEXT', 'STREET'),
        Column('zip', 'INTEGER', 'ZIPCODE'),
        Column('boro', 'TEXT', 'BORO'),
        Column('phone', 'INTEGER', 'PHONE'),
        Column('name', 'TEXT', 'DBA'), # DBA = 'doing business as'
        Column('cuisine', 'TEXT', 'CUISINE'),
        Column('nyc_id', 'INTEGER', 'CAMIS') # CAMIS = NYC UID
    ]
)

"""
Example code:
'06C'
Example description:
'Food not protected from potential source of contamination.'
"""
violation_table = Table('r_violation')
violation_table.add_columns(
    [
        Column('id', 'INTEGER PRIMARY KEY AUTOINCREMENT'),
        Column('code', 'TEXT', 'VIOLATION CODE'),
        Column('description', 'TEXT', 'VIOLATION DESCRIPTION')
    ]
)


"""
Example description: 'Establishment re-opened by DOHMH'
"""
action_table = Table('r_action')
action_table.add_columns(
    [
        Column('id', 'INTEGER PRIMARY KEY AUTOINCREMENT'),
        Column('description', 'TEXT', 'ACTION')
    ]
)

"""
Example raw inspection value:
'Trans Fat / Compliance Inspection'

The part before the slash is the compliance area the inspector
was scrutinizing (the 'inspection subject'). The part after the
slash is the broad class of inspection that was conducted (
the 'inspection type'). These two values vary independently, so
they are added to their own tables.

It's alright to blindly split on the '/'; none of values have
additional forward slashes.
"""
inspection_subject_table = Table('r_inspection_subject')
inspection_subject_table.add_columns(
    [
        Column('id', 'INTEGER PRIMARY KEY AUTOINCREMENT'),
        Column('subject', 'TEXT')
    ]
)

inspection_type_table = Table('r_inspection_type')
inspection_type_table.add_columns(
    [
        Column('id', 'INTEGER PRIMARY KEY AUTOINCREMENT'),
        Column('type', 'TEXT')
    ]
)

"""
Holds actual inspection event records
"""
inspection_event_table = Table('r_inspection_event')
inspection_event_table.add_columns(
    [
        Column('id', 'INTEGER PRIMARY KEY AUTOINCREMENT'),
        Column('restaurant_id', 'INTEGER'),
        Column('violation_id', 'INTEGER'),
        Column('type_id', 'INTEGER'),
        Column('subject_id', 'INTEGER'),
        Column('action_id', 'INTEGER'),
        Column('score', 'INTEGER', 'SCORE'),
        Column('grade', 'TEXT', 'GRADE'),
        Column('flag', 'TEXT', 'CRITICAL FLAG'),
        Column('inspection_date', 'DATE', 'INSPECTION DATE'),
        Column('grade_date', 'DATE', 'GRADE DATE')
    ]
)
inspection_event_table.add_foreign_keys(
    [
        ForeignKey('restaurant_id', restaurant_table, 'id'),
        ForeignKey('violation_id', violation_table, 'id'),
        ForeignKey('type_id', inspection_type_table, 'id'),
        ForeignKey('subject_id', inspection_subject_table, 'id'),
        ForeignKey('action_id', action_table, 'id')
    ]
)


all_tables = (
    restaurant_table,
    violation_table,
    action_table,
    inspection_subject_table,
    inspection_type_table,
    inspection_event_table
)
