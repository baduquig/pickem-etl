"""
Pickem ETL
Author: Gabe Baduqui

Cleanse, format and prepare Teams data
"""

def transform_conference_name(conference_name_raw: str, transform_logfile: object):
    """Function that extracts just the name of a conference from the given standings header string
       Accepts `conference_name_raw`: String, `transform_logfile`: File Object
       Returns `conference_name`: String"""
    transform_logfile.write(f'Transforming conference name {conference_name_raw} -> ')

    try:
        year = conference_name_raw.split(' ')[0]
        conference_name = conference_name_raw.replace(year, '').replace('Standings', '').lstrip().rstrip()
        transform_logfile.write(f'{conference_name}\n')
    except Exception as e:
        conference_name = 'TBD'
        transform_logfile.write(f'{e}\n')

    return conference_name

def transform_record(record_raw: str, transform_logfile: object):
    """Function that transforms record elements into individual fields
       Accepts `record_raw`: String, `transform_logfile`: File Object
       Returns `wins`: Number, `losses`: Number, `ties`: Number,"""
    transform_logfile.write(f'Transforming record {record_raw} -> ')
    
    try:
        record_elements = record_raw.split('-')
        wins = int(record_elements[0])
        losses = int(record_elements[1])
        if len(record_elements) > 2:
            ties = int(record_elements[2])
        else:
            ties = 0
        transform_logfile.write(f'{wins}, {losses}, {ties}\n')
    except Exception as e:
        wins = 0
        losses = 0
        ties = 0
        transform_logfile.write(f'{e}\n{record_raw}\n')

    return wins, losses, ties