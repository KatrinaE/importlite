from dbimport.schema import Table, Column, ForeignKey

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

def split_inspection_subject(inspection_str):
    inspection_tuple = inspection_str.split('/')
    inspection_subject = inspection_tuple[0]
    return inspection_subject

inspection_subject_table.add_columns(
    [
        Column('id', 'INTEGER PRIMARY KEY AUTOINCREMENT'),
        Column('subject', 'TEXT', 'INSPECTION TYPE',
               split_inspection_subject)
    ]
)

inspection_type_table = Table('r_inspection_type')

def split_inspection_type(inspection_str):
    inspection_tuple = inspection_str.split('/')
    inspection_type = inspection_tuple[1]
    return inspection_type

inspection_type_table.add_columns(
    [
        Column('id', 'INTEGER PRIMARY KEY AUTOINCREMENT'),
        Column('type', 'TEXT', 'INSPECTION TYPE',
               split_inspection_type)
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
