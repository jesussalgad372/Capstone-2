"""
Module determining pilot certifications, ratings, and endorsements.

The restrictions that we place on a pilot depend on their qualifications.  There are three
ways to think about a pilot.  

(1) Certifications.  These are what licenses a pilot has.  We also use these to classify
where the student is in the licensing process.  Is the student post solo (can fly without
instructor), but before license?  Is the student 50 hours past their license (a threshold 
that helps with insurance)?

(2) Ratings.  These are extra add-ons that a pilot can add to a license. For this project,
the only rating is Instrument Rating, which allows a pilot to fly through adverse weather
using only instruments.

(3) Endorsements. These are permission to fly certain types of planes solo.  Advanced 
allows a pilot to fly a plane with retractable landing gear. Multiengine allows a pilot
to fly a plane with more than one engine.

The file pilots.csv is a list of all pilots in the school, together with the dates that
they earned these certifications, ratings, and endorsements.  Specifically, this CSV file
has the following header:
    
    ID  LASTNAME  FIRSTNAME  JOINED  SOLO  LICENSE  50 HOURS  INSTRUMENT  ADVANCED  MULTIENGINE

The first three columns are strings, while all other columns are dates.

The functions in this class take a row from the pilot table and determine if a pilot has
a certain qualification at the time of takeoff. As this program is auditing the school 
over a course of a year, a student may not be instrument rated for one flight but might
be for another.

The preconditions for many of these functions are quite messy.  While this makes writing 
the functions simpler (because the preconditions ensure we have less to worry about), 
enforcing these preconditions can be quite hard. That is why it is not necessary to 
enforce any of the preconditions in this module.

Author: Jesus Salgado
Date: 6/24/2025
"""
import utils


# CERTIFICATION CLASSIFICATIONS
# The certification of this pilot is unknown
PILOT_INVALID = -1
# A pilot that has joined the school, but has not soloed
PILOT_NOVICE  = 0
# A pilot that has soloed but does not have a license
PILOT_STUDENT = 1
# A pilot that has a license, but has under 50 hours post license
PILOT_CERTIFIED = 2
# A pilot that 50 hours post license
PILOT_50_HOURS  = 3


def get_certification(takeoff,student):
    """
    Returns the certification classification for this student at the time of takeoff.
    
    The certification is represented by an int, and must be the value PILOT_NOVICE, 
    PILOT_STUDENT, PILOT_CERTIFIED, PILOT_50_HOURS, or PILOT_INVALID. It is PILOT_50_HOURS 
    if the student has certified '50 Hours' before this flight takeoff.  It is 
    PILOT_CERTIFIED if the student has a private license before this takeoff and 
    PILOT_STUDENT if the student has soloed before this takeoff.  A pilot that has only
    just joined the school is PILOT_NOVICE.  If the flight takes place before the student
    has even joined the school, the result is PILOT_INVALID.
    
    Recall that a student is a 10-element list of strings.  The first three elements are
    the student's identifier, last name, and first name.  The remaining elements are all
    timestamps indicating the following in order: time joining the school, time of first 
    solo, time of private license, time of 50 hours certification, time of instrument 
    rating, time of advanced endorsement, and time of multiengine endorsement.
    
    Parameter takeoff: The takeoff time of this flight
    Precondition: takeoff is a datetime object with a time zone
    
    Parameter student: The student pilot
    Precondition: student is 10-element list of strings representing a pilot
    """
    # Indices for each date in the student list
    IDX_JOINED = 3
    IDX_SOLO = 4
    IDX_LICENSE = 5
    IDX_50HOURS = 6

    # Helper to parse a date string (returns None if empty or invalid)
    def parse_date(date_str):
        if not date_str:
            return None
        dt = utils.str_to_time(date_str, takeoff.tzinfo)
        # If dt is naive, assign takeoff's timezone
        if dt is not None and dt.tzinfo is None:
            dt = dt.replace(tzinfo=takeoff.tzinfo)
        return dt

    # Parse all relevant dates
    joined = parse_date(student[IDX_JOINED])
    solo = parse_date(student[IDX_SOLO])
    license = parse_date(student[IDX_LICENSE])
    hours50 = parse_date(student[IDX_50HOURS])

    # If takeoff is before joining, invalid
    if joined is None or takeoff < joined:
        return PILOT_INVALID
    # 50 hours certified before takeoff
    if hours50 is not None and takeoff >= hours50:
        return PILOT_50_HOURS
    # Licensed before takeoff
    if license is not None and takeoff >= license:
        return PILOT_CERTIFIED
    # Soloed before takeoff
    if solo is not None and takeoff >= solo:
        return PILOT_STUDENT
    # Joined but not soloed
    if joined is not None and takeoff >= joined:
        return PILOT_NOVICE
    # Fallback (should not reach here)
    return PILOT_INVALID



def has_instrument_rating(takeoff,student):
    """
    (OPTIONAL)
    Returns True if the student has an instrument rating at the time of takeoff, False otherwise
    
    Recall that a student is a 10-element list of strings.  The first three elements are
    the student's identifier, last name, and first name.  The remaining elements are all
    timestamps indicating the following in order: time joining the school, time of first 
    solo, time of private license, time of 50 hours certification, time of instrument 
    rating, time of advanced endorsement, and time of multiengine endorsement.
    
    NOTE: Just because a pilot has an instrument rating does not mean that every flight
    with that pilot is an IFR flight.  It just means the pilot could choose to use VFR
    or IFR rules.
    
    Parameter takeoff: The takeoff time of this flight
    Precondition: takeoff is a datetime object
    
    Parameter student: The student pilot
    Precondition: student is 10-element list of strings representing a pilot
    """
    # Index for instrument rating in the student list
    IDX_INSTRUMENT = 7

    # Get the instrument rating date string
    instrument_str = student[IDX_INSTRUMENT]

    # If there is no instrument rating date, return False
    if not instrument_str:
        return False

    # Parse the instrument rating date, using the timezone from takeoff if needed
    instrument_date = utils.str_to_time(instrument_str, takeoff.tzinfo)

    # If parsing failed, treat as no rating
    if instrument_date is None:
        return False

    # Ensure both datetimes are timezone-aware or both are naive
    if instrument_date.tzinfo is None and takeoff.tzinfo is not None:
        instrument_date = instrument_date.replace(tzinfo=takeoff.tzinfo)
    elif instrument_date.tzinfo is not None and takeoff.tzinfo is None:
        takeoff = takeoff.replace(tzinfo=instrument_date.tzinfo)

    # If the rating was earned on or before takeoff, return True
    return takeoff >= instrument_date


def has_advanced_endorsement(takeoff,student):
    """
    (OPTIONAL)
    Returns True if the student has an endorsement to fly an advanced plane at the time of takeoff.
    
    The function returns False otherwise.
    
    Recall that a student is a 10-element list of strings.  The first three elements are
    the student's identifier, last name, and first name.  The remaining elements are all
    timestamps indicating the following in order: time joining the school, time of first 
    solo, time of private license, time of 50 hours certification, time of instrument 
    rating, time of advanced endorsement, and time of multiengine endorsement.
    
    Parameter takeoff: The takeoff time of this flight
    Precondition: takeoff is a datetime object
    
    Parameter student: The student pilot
    Precondition: student is 10-element list of strings representing a pilot
    """
    #Index for advanced endorsement in the student list
    IDX_ADVANCED = 8

    #Get the advanced endorsement date string
    advanced_str = student[IDX_ADVANCED]

    #If there is no advanced endorsement date, return False
    if not advanced_str:
        return False

    #Parse the advanced endorsement date, using the timezone from takeoff if needed
    advanced_date = utils.str_to_time(advanced_str, takeoff.tzinfo)

    #If parsing failed, treat as no endorsement
    if advanced_date is None:
        return False

    # Ensure both datetimes are timezone-aware or both are naive
    if advanced_date.tzinfo is None and takeoff.tzinfo is not None:
        advanced_date = advanced_date.replace(tzinfo=takeoff.tzinfo)
    elif advanced_date.tzinfo is not None and takeoff.tzinfo is None:
        takeoff = takeoff.replace(tzinfo=advanced_date.tzinfo)

    #If the endorsement was earned on or before takeoff, return True
    return takeoff >= advanced_date


def has_multiengine_endorsement(takeoff,student):
    """
    (OPTIONAL)
    Returns True if the student has an endorsement to fly an multiengine plane at the time of takeoff.
    
    The function returns False otherwise.
    
    Recall that a student is a 10-element list of strings.  The first three elements are
    the student's identifier, last name, and first name.  The remaining elements are all
    timestamps indicating the following in order: time joining the school, time of first 
    solo, time of private license, time of 50 hours certification, time of instrument 
    rating, time of advanced endorsement, and time of multiengine endorsement.
    
    Parameter takeoff: The takeoff time of this flight
    Precondition: takeoff is a datetime object
    
    Parameter student: The student pilot
    Precondition: student is 10-element list of strings representing a pilot
    """
    # Index for multiengine endorsement in the student list
    IDX_MULTIENGINE = 9

    # Get the multiengine endorsement date string
    multi_str = student[IDX_MULTIENGINE]

    # If there is no multiengine endorsement date, return False
    if not multi_str:
        return False

    # Parse the multiengine endorsement date, using the timezone from takeoff if needed
    multi_date = utils.str_to_time(multi_str, takeoff.tzinfo)

    # If parsing failed, treat as no endorsement
    if multi_date is None:
        return False

    # Ensure both datetimes are timezone-aware or both are naive
    if multi_date.tzinfo is None and takeoff.tzinfo is not None:
        multi_date = multi_date.replace(tzinfo=takeoff.tzinfo)
    elif multi_date.tzinfo is not None and takeoff.tzinfo is None:
        takeoff = takeoff.replace(tzinfo=multi_date.tzinfo)

    # If the endorsement was earned on or before takeoff, return True
    return takeoff >= multi_date


def get_best_value(data, index, maximum=True):
    """
    Returns the 'best' value from a given column in a 2-dimensional nested list.
    
    This function is a helper function for get_minimums (whose docstring you should
    read and understand first). 
    
    The data parameter is a 2-dimensional nested list of data.  The index parameter
    indicates which "colummn" of data should be evaluated. Each item in that column
    is expected to be a number in string format.  Each item should be evaluated as a 
    float and the best value selected as the return value for the function. The
    best value is determined by the maximum parameter and is either the highest or
    lowest float value.

    The 2D list does not include a header row. It should not be modified in any way.
    
    Parameter data: a 2-dimensional nested list of data
    Precondition: the column referenced by index should by numbers in string format
    
    Parameter index: position to examine in each row of data
    Precondition: index is a an integer
    
    Parameter maximum: indicates whether to return the highest value (True) or
    lowest value (False)
    Precondition: maximum is a boolean and defaults to True
    
    """
    #Extract the values from the specified column and convert them to floats
    values = []
    for row in data:
        value = float(row[index]) #Convert string to float
        values.append(value)

    #Return the maximum or minimum value, depending on the 'maximum' flag
    if maximum:
        return max(values)
    else:
        return min(values)


def get_minimums(cert, area, instructed, vfr, daytime, minimums):
    """
    Returns the most advantageous minimums for the given flight category.
    
    The minimums is the 2-dimensional list (table) of minimums, including the header.
    The header for this table is as follows:
        
        CATEGORY  CONDITIONS  AREA  TIME  CEILING  VISIBILITY  WIND  CROSSWIND
    
    The values in the first four columns are strings, while the values in the last
    four columns are numbers.  CEILING is a measurement in ft, while VISIBILITY is in
    miles.  Both WIND and CROSSWIND are speeds in knots.
    
    This function first searches the table for rows that match the function parameters. 
    It is possible for more than one row to be a match.  A row is a match if ALL four 
    of the first four columns match.
    
    The first column (CATEGORY) has values 'Student', 'Certified', '50 Hours', or 'Dual'.
    If the value 'Student', it is a match if cert is PILOT_STUDENT or higher.  If the
    value is 'Certified', it is a match if cert is PILOT_CERTIFIED or higher. If it is 
    '50 Hours', it is only a match if cert is PILOT_50_HOURS. The value 'Dual' only
    matches if instructed is True and even if cert is PILOT_INVALID or PILOT_NOVICE.
    
    The second column (CONDITIONS) has values 'VMC' and 'IMC'. A flight filed as VFR 
    (visual flight rules) is subject to VMC (visual meteorological conditions) minimums.  
    Similarly, a fight filed as IFR is subject to IMC minimums.
    
    The third column (AREA) has values 'Pattern', 'Practice Area', 'Local', 
    'Cross Country', or 'Any'. Flights that are in the pattern or practice area match
    'Local' as well.  All flights match 'Any'.
    
    The fourth column (TIME) has values 'Day' or 'Night'. The value 'Day' is only 
    a match if daytime is True. If it is False, 'Night' is the only match.
    
    Once the function finds the all matching rows, it searches for the most advantageous
    values for CEILING, VISIBILITY, WIND, and CROSSWIND. Lower values of CEILING and
    VISIBILITY are better.  Higher values for WIND and CROSSWIND are better.  It then
    returns this four values as a list of four floats (in the same order they appear)
    in the table.
    
    Example: Suppose minimums is the table
        
        CATEGORY   CONDITIONS  AREA           TIME  CEILING  VISIBILITY  WIND  CROSSWIND
        Student    VMC         Pattern        Day   2000     5           20    8
        Student    VMC         Practice Area  Day   3000     10          20    8
        Certified  VMC         Local          Day   3000     5           20    20
        Certified  VMC         Practice Area  Night 3000     10          20    10
        50 Hours   VMC         Local          Day   3000     10          20    10
        Dual       VMC         Any            Day   2000     10          30    10
        Dual       IMC         Any            Day   500      0.75        30    20
    
    The call get_minimums(PILOT_CERTIFIED,'Practice Area',True,True,True,minimums) matches
    all of the following rows:
        
        Student    VMC         Practice Area  Day   3000     10          20    8
        Certified  VMC         Local          Day   3000     5           20    20
        Dual       VMC         Any            Day   2000     10          30    10
    
    The answer in this case is [2000,5,30,20]. 2000 and 5 are the least CEILING and 
    VISIBILITY values while 30 and 20 are the largest wind values.
    
    If there are no rows that match the parameters (e.g. a novice pilot with no 
    instructor), this function returns None.
    
    Parameter cert: The pilot certification
    Precondition: cert is an int and one of PILOT_NOVICE, PILOT_STUDENT, PILOT_CERTIFIED, 
    PILOT_50_HOURS, or PILOT_INVALID.
    
    Parameter area: The flight area for this flight plan
    Precondition: area is a string and one of 'Pattern', 'Practice Area' or 'Cross Country'
    
    Parameter instructed: Whether an instructor is present
    Precondition: instructed is a boolean
    
    Parameter vfr: Whether the pilot has filed this as an VFR flight
    Precondition: vfr is a boolean
    
    Parameter daytime: Whether this flight is during the day
    Precondition: daytime is boolean
    
    Parameter minimums: The table of allowed minimums
    Precondition: minimums is a 2d-list (table) as described above, including header
    """
    # Indices for columns in the minimums table
    IDX_CATEGORY = 0
    IDX_CONDITIONS = 1
    IDX_AREA = 2
    IDX_TIME = 3
    IDX_CEILING = 4
    IDX_VISIBILITY = 5
    IDX_WIND = 6
    IDX_CROSSWIND = 7

    # Remove header row for processing
    data = minimums[1:]

    matches = []
    for row in data:
        # CATEGORY matching
        cat = row[IDX_CATEGORY]
        if cat == 'Dual':
            if not instructed:
                continue  # Only match if instructor is present
        elif cat == '50 Hours':
            if cert != PILOT_50_HOURS:
                continue
        elif cat == 'Certified':
            if cert < PILOT_CERTIFIED:
                continue
        elif cat == 'Student':
            if cert < PILOT_STUDENT:
                continue

        # CONDITIONS matching
        cond = row[IDX_CONDITIONS]
        if vfr and cond != 'VMC':
            continue
        if not vfr and cond != 'IMC':
            continue

        # AREA matching
        area_val = row[IDX_AREA]
        # Flights in 'Pattern' or 'Practice Area' also match 'Local'
        if area_val == 'Any':
            pass  # Always matches
        elif area_val == 'Local':
            if area not in ['Pattern', 'Practice Area', 'Local']:
                continue
        elif area_val != area:
            continue

        # TIME matching
        time_val = row[IDX_TIME]
        if daytime and time_val != 'Day':
            continue
        if not daytime and time_val != 'Night':
            continue

        # If all checks passed, add to matches
        matches.append(row)

    # If no matches found, return None
    if not matches:
        return None

    # Find the best values for each column using get_best_value
    ceiling = get_best_value(matches, IDX_CEILING, maximum=False)      # Lower is better
    visibility = get_best_value(matches, IDX_VISIBILITY, maximum=False)  # Lower is better
    wind = get_best_value(matches, IDX_WIND, maximum=True)             # Higher is better
    crosswind = get_best_value(matches, IDX_CROSSWIND, maximum=True)   # Higher is better

    # Return the four values as a list of floats
    return [ceiling, visibility, wind, crosswind]

