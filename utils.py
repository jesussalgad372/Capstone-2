"""
Module providing utility functions for this project.

These functions are general purpose utilities used by other modules in this project.
Some of these functions were exercises in early course modules and should be copied
over into this file.

The preconditions for many of these functions are quite messy.  While this makes writing 
the functions simpler (because the preconditions ensure we have less to worry about), 
enforcing these preconditions can be quite hard. That is why it is not necessary to 
enforce any of the preconditions in this module.

Author: Jesus Salgado
Date: 6/24/2025
"""
import csv
import json
import datetime
from dateutil import parser
import pytz


def read_csv(filename):
    """
    Returns the contents read from the CSV file filename.
    
    This function reads the contents of the file filename and returns the contents as
    a 2-dimensional list. Each element of the list is a row, with the first row being
    the header. Cells in each row are all interpreted as strings; it is up to the 
    programmer to interpret this data, since CSV files contain no type information.
    
    Parameter filename: The file to read
    Precondition: filename is a string, referring to a file that exists, and that file 
    is a valid CSV file
    """
    result = []
    #Open the file with the universal newline support and UTF-8 encoding
    with open(filename, newline='', encoding='utf-8') as csvfile:
        reader = csv.reader(csvfile)  #Create a CSV reader object
        for row in reader:
            result.append(row)      #Add each row (as a list of strings) to result
    #Result the 2D list of rows (including header as first row)
    return result


def write_csv(data,filename):
    """
    Writes the given data out as a CSV file filename.
    
    To be a proper CSV file, data must be a 2-dimensional list with the first row 
    containing only strings.  All other rows may be any Python value.  Dates are
    converted using ISO formatting. All other objects are converted to their string
    representation.
    
    Parameter data: The Python value to encode as a CSV file
    Precondition: data is a  2-dimensional list of strings
    
    Parameter filename: The file to read
    Precondition: filename is a string representing a path to a file with extension
    .csv or .CSV.  The file may or may not exist.
    """
    # Open the file for writing with UTF-8 encoding and universal newline support
    with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.writer(csvfile)  # Create a CSV writer object
        for row in data:
            out_row = []
            for item in row:
                # If the item is a date or datetime, convert to ISO format string
                if isinstance(item, datetime.date):
                    out_row.append(item.isoformat())
                else:
                    # Otherwise, convert the item to a string
                    out_row.append(str(item))
            writer.writerow(out_row)  # Write the processed row to the CSV file
    # File is automatically closed after the with-block


def read_json(filename):
    """
    Returns the contents read from the JSON file filename.
    
    This function reads the contents of the file filename, and will use the json module
    to covert these contents in to a Python data value.  This value will either be a
    a dictionary or a list. 
    
    Parameter filename: The file to read
    Precondition: filename is a string, referring to a file that exists, and that file 
    is a valid JSON file
    """
    #Open the file for reading with UTF-8 encoding
    with open(filename, 'r', encoding='utf-8') as file:
        data = json.load(file)  #Load and parse the JSON data into a Python object
    return data


def str_to_time(timestamp,tzsource=None):
    """
    Returns the datetime object for the given timestamp (or None if timestamp is 
    invalid).
    
    This function should just use the parse function in dateutil.parser to
    convert the timestamp to a datetime object.  If it is not a valid date (so
    the parser crashes), this function should return None.
    
    If the timestamp has a time zone, then it should keep that time zone even if
    the value for tzsource is not None.  Otherwise, if timestamp has no time zone 
    and tzsource is not None, then this function will use tzsource to assign 
    a time zone to the new datetime object.
    
    The value for tzsource can be None, a string, or a datetime object.  If it 
    is a string, it will be the name of a time zone, and it should localize the 
    timestamp.  If it is another datetime, then the datetime object created from 
    timestamp should get the same time zone as tzsource.
    
    Parameter timestamp: The time stamp to convert
    Precondition: timestamp is a string
    
    Parameter tzsource: The time zone to use (OPTIONAL)
    Precondition: tzsource is either None, a string naming a valid time zone,
    or a datetime object.
    """
    try:
        # Parse the timestamp string into a datetime object
        dt = parser.parse(timestamp)
    except Exception:
        # Return None if parsing fails
        return None

    # If the parsed datetime already has a timezone, return as is
    if dt.tzinfo is not None:
        return dt

    # If no timezone and tzsource is provided, assign a timezone
    if tzsource is not None:
        if isinstance(tzsource, str):
            # tzsource is a string: use pytz to get the timezone and localize
            tz = pytz.timezone(tzsource)
            dt = tz.localize(dt)
        elif hasattr(tzsource, 'tzinfo') and tzsource.tzinfo is not None:
            # tzsource is a datetime object with tzinfo: use its timezone
            dt = dt.replace(tzinfo=tzsource.tzinfo)
        # If tzsource is a datetime without tzinfo, do nothing (leave naive)
    return dt


def daytime(time,daycycle):
    """
    Returns true if the time takes place during the day.
    
    A time is during the day if it is after sunrise but before sunset, as
    indicated by the daycycle dicitionary.
    
    A daycycle dictionary has keys for several years (as int).  The value for
    each year is also a dictionary, taking strings of the form 'mm-dd'.  The
    value for that key is a THIRD dictionary, with two keys "sunrise" and
    "sunset".  The value for each of those two keys is a string in 24-hour
    time format.
    
    For example, here is what part of a daycycle dictionary might look like:
    
        "2015": {
            "01-01": {
                "sunrise": "07:35",
                "sunset":  "16:44"
            },
            "01-02": {
                "sunrise": "07:36",
                "sunset":  "16:45"
            },
            ...
        }
    
    In addition, the daycycle dictionary has a key 'timezone' that expresses the
    timezone as a string. This function uses that timezone when constructing
    datetime objects from this set.  If the time parameter does not have a timezone,
    we assume that it is in the same timezone as the daycycle dictionary
    
    Parameter time: The time to check
    Precondition: time is a datetime object
    
    Parameter daycycle: The daycycle dictionary
    Precondition: daycycle is a valid daycycle dictionary, as described above
    """
    # Get the year and mm-dd string for lookup
    year = str(time.year)
    mm_dd = time.strftime('%m-%d')

    # Get the timezone from the daycycle dictionary
    tzname = daycycle.get('timezone')
    if tzname is None:
        return None  # No timezone info

    # Check if year and date exist in the daycycle dictionary
    if year not in daycycle or mm_dd not in daycycle[year]:
        return None  # Missing data for this date

    # Get sunrise and sunset strings
    sunrise_str = daycycle[year][mm_dd].get('sunrise')
    sunset_str = daycycle[year][mm_dd].get('sunset')
    if sunrise_str is None or sunset_str is None:
        return None  # Missing sunrise or sunset

    # Build ISO datetime strings for sunrise and sunset
    date_str = time.date().isoformat()
    sunrise_iso = f"{date_str}T{sunrise_str}"
    sunset_iso = f"{date_str}T{sunset_str}"

    # Convert sunrise and sunset to datetime objects with correct timezone
    sunrise = str_to_time(sunrise_iso, tzname)
    sunset = str_to_time(sunset_iso, tzname)

    # If conversion failed, return None
    if sunrise is None or sunset is None:
        return None

    # Get the timezone object
    tz = pytz.timezone(tzname)

    # Convert all times to the same timezone for comparison
    if time.tzinfo is None:
        time = tz.localize(time)
    else:
        time = time.astimezone(tz)
    sunrise = sunrise.astimezone(tz)
    sunset = sunset.astimezone(tz)

    # Return True if time is during the day, False otherwise
    return sunrise < time < sunset


def get_for_id(id,table):
    """
    Returns (a copy of) a row of the table with the given id.
    
    Table is a two-dimensional list where the first element of each row is an identifier
    (string).  This function searches table for the row with the matching identifier and
    returns a COPY of that row. If there is no match, this function returns None.
    
    This function is useful for extract rows from a table of pilots, a table of instructors,
    or even a table of planes.
    
    Parameter id: The id of the student or instructor
    Precondition: id is a string
    
    Parameter table: The 2-dimensional table of data
    Precondition: table is a non-empty 2-dimension list of strings
    """
    #Iterate through each row in the table
    for row in table:
        #Check if the first element (identifier) mathces the given id
        if row[0] == id:
            return row.copy() # Return a copy of the matching row
    #If no matching row is found, return None
    return None
