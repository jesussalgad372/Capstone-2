"""
Module to check violations for a flight lesson.

This module processes the primary violations, which are violations of weather restrictions. 
Weather restrictions express the minimum conditions that a pilot is allowed to fly in.  
So if a pilot has a ceiling minimum of 2000 feet, and there is cloud cover at 1500 feet, 
the pilot should not fly.To understand weather minimums, you have to integrate three 
different files: daycycle.json (for sunrise and sunset), weather.json (for hourly weather 
observations at the airport), and minimums.csv (for the schools minimums set by agreement 
with the insurance agency). You should look at those files BRIEFLY to familiarize yourself 
with them.

This module can get overwhelming if you panic and think too much about the big picture.  
Like a good software developer, you should focus on the specifications and do a little
at a time.  While these functions may seem like they require a lot of FAA knowledge, all
of the information you need is in the specifications. They are complex specifications,
but all of the information you need is there.  Combined with the provided unit tests
in tests.py, this assignment is very doable.

It may seem weird that these functions only check weather conditions at the time of 
takeoff and not the entire time the flight is in the air.  This is standard procedure 
for this insurance company.  The school is only liable if they let a pilot take off in 
the wrong conditions.  If the pilot stays up in adverse conditions, responsibility shifts 
to the pilot.

The preconditions for many of these functions are quite messy.  While this makes writing 
the functions simpler (because the preconditions ensure we have less to worry about), 
enforcing these preconditions can be quite hard. That is why it is not necessary to 
enforce any of the preconditions in this module.

Author: Jesus Salgado
Date: 6/24/2025
"""
import utils
import pilots
import os.path


# WEATHER FUNCTIONS
def bad_visibility(visibility,minimum):
    """
    Returns True if the visibility measurement violates the minimum, False otherwise
    
    A valid visibility measurement is EITHER the string 'unavailable', or a dictionary 
    with (up to) four values: 'minimum', 'maximum',  'prevailing', and 'units'. Only 
    'prevailing' and 'units' are required; the other two are optional. The units may be 
    'FT' (feet) or 'SM' for (statute) miles, and explain how to interpret other three 
    fields, which are all floats.
    
    This function should compare ths visibility 'minimum' (if it exists) against the 
    minimum parameter. Else it compares the 'prevailing' visibility. This function returns
    True if minimum is more than the measurement. If the visibility is 'unavailable', 
    then this function returns True (indicating bad record keeping).
    
    Example: Suppose we have the following visibility measurement.
        
        {
            "prevailing": 21120.0,
            "minimum": 1400.0,
            "maximum": 21120.0,
            "units": "FT"
        }
    
    Given the above measurement, this function returns True if visibility is 0.25 (miles)
    and False if it is 1.
    
    Parameter visibility: The visibility information
    Precondition: visibility is a valid visibility measurement, as described above.
    (e.g. either a dictionary or the string 'unavailable')
    
    Parameter minimum: The minimum allowed visibility (in statute miles)
    Precondition: minimum is a float or int
    """
    # If visibility is 'unavailable', always return True (bad record keeping)
    if visibility == 'unavailable':
        return True

    # If visibility is a dictionary, process the values
    if isinstance(visibility, dict):
        # Use 'minimum' if it exists and is not None, otherwise use 'prevailing'
        if 'minimum' in visibility and visibility['minimum'] is not None:
            value = visibility['minimum']
        else:
            value = visibility['prevailing']

        # Convert value to statute miles if needed
        if visibility['units'] == 'FT':
            value = value / 5280.0  # Convert feet to statute miles

        # Return True if the minimum is greater than the measured value (violation)
        return value < minimum

    # If visibility is not a recognized type, treat as violation (conservative)
    return True


def bad_winds(winds,maxwind,maxcross):
    """
    Returns True if the wind measurement violates the maximums, False otherwise
    
    A valid wind measurement is EITHER the string 'calm', the string 'unavailable' or 
    a dictionary with (up to) four values: 'speed', 'crosswind', 'gusts', and 'units'. 
    Only 'speed' and 'units' are required if it is a dictionary; the other two are 
    optional. The units are either be 'KT' (knots) or 'MPS' (meters per second), and 
    explain how to interpret other three fields, which are all floats.
    
    This function should compare 'speed' or 'gusts' against the maxwind parameter
    (whichever is worse) and 'crosswind' against the maxcross. If either measurement is greater
    than the allowed maximum, this function returns True.
    
    If the winds are 'calm', then this function always returns False. If the winds are
    'unavailable', then this function returns True (indicating bad record keeping).
    
    For conversion information, 1 MPS is roughly 1.94384 knots.
    
    Example: Suppose we have the following wind measurement.
        
        {
            "speed": 12.0,
            "crosswind": 10.0,
            "gusts": 18.0,
            "units": "KT"
        }
    
    Given the above measurement, this function returns True if maxwind is 15 or maxcross is 5.
    If both maxwind is 20 and maxcross is 10, it returns False.  (If 'units' were 'MPS'
    it would be false in both cases).
    
    Parameter winds: The wind speed information
    Precondition: winds is a valid wind measurement, as described above.
    (e.g. either a dictionary, the string 'calm', or the string 'unavailable')
    
    Parameter maxwind: The maximum allowable wind speed (in knots)
    Precondition: maxwind is a float or int
    
    Parameter maxcross: The maximum allowable crosswind speed (in knots)
    Precondition: maxcross is a float or int
    """
    #If winds are 'calm', always return False (no violation)
    if winds == 'calm':
        return False

    #If winds are 'unavailable', always return True (bad record keeping)
    if winds == 'unavailable':
        return True

    #If winds is a dictionary, process the values
    if isinstance(winds, dict):
        #Extract speed and gusts (gusts is optional)
        speed = winds.get('speed', 0.0)
        gusts = winds.get('gusts', speed) #If gusts not present use speed
        crosswind = winds.get('crosswind', 0.0)
        units = winds.get('units', 'KT')

        #Convert all values to knots if needed
        if units == 'MPS':
            speed = speed * 1.94384
            gusts = gusts * 1.94384
            crosswind = crosswind * 1.94384

        #Use the worst wind (max of speed and gusts)
        worst_wind = max(speed, gusts)

        #Check if either wind or crosswind exceeds the maximums
        if worst_wind > maxwind or crosswind > maxcross:
            return True
        else:
            return False

    #If winds is not a recognized type, treat a violation (conservative)
    return True
    

def bad_ceiling(ceiling,minimum):
    """
    Returns True if the ceiling measurement violates the minimum, False otherwise
    
    A valid ceiling measurement is EITHER the string 'clear', the string 'unavailable', 
    or a list of cloud layer measurements. A cloud layer measurement is a dictionary with 
    three required keys: 'type', 'height', and 'units'.  Type is one of 'a few', 
    'scattered', 'broken', 'overcast', or 'indefinite ceiling'. The value 'units' must 
    be 'FT', and specifies the units for the float associated with 'height'.
    
    If the ceiling is 'clear', then this function always returns False. If the ceiling 
    is 'unavailable', then this function returns True (indicating bad record keeping).
    Otherwise, it compares the minimum allowed ceiling against the lowest cloud layer 
    that is either 'broken', 'overcast', or 'indefinite ceiling'. If the only type of
    cloud layer is 'a few' or 'scattered', then this function should return False.
    
    Example: Suppose we have the following ceiling measurement.
        
        [
            {
                "cover": "clouds",
                "type": "scattered",
                "height": 700.0,
                "units": "FT"
            },
            {
                "type": "overcast",
                "height": 1200.0,
                "units": "FT"
            }
        ]
    
    Given the above measurement, this function returns True if minimum is 2000,
    but False if it is 1000.
    
    Parameter ceiling: The ceiling information
    Precondition: ceiling is a valid ceiling measurement, as described above.
    (e.g. either a dictionary, the string 'clear', or the string 'unavailable')
        
    Parameter minimum: The minimum allowed ceiling (in feet)
    Precondition: minimum is a float or int
    """
    #If ceiling is 'clear', always return False (no violation)
    if ceiling == 'clear':
        return False

    #If ceiling is 'unavailable', always return True (bad record keeping)
    if ceiling == 'unavailable':
        return True

    #If ceiling is a  list of cloud layers, process the layers
    if isinstance(ceiling, list):
        #List to store heights of relevant cloud layers
        relevant_heights = []
        for layer in ceiling:
            #Only consider 'broken', 'overcast', or 'indefinite ceiling'
            if layer.get('type') in ['broken', 'overcast', 'indefinite ceiling']:
                #Ensure units are 'FT' as required
                if layer.get('units') == 'FT':
                    relevant_heights.append(layer.get('height'))
        #If there are no relevant layers, return False (no violation)
        if not relevant_heights:
            return False
        #Find the lowest relevant cloud layer
        lowest = min(relevant_heights)
        #Return True if the minimum is greater than the lowest layer (violation)
        return lowest < minimum
    
    #If ceiling is not a recognized type, treat as a violation (conservative)
    return True


def get_weather_report(takeoff,weather):
    """
    Returns the most recent weather report at or before take-off.
    
    The weather is a dictionary whose keys are ISO formatted timestamps and whose values 
    are weather reports.  For example, here is an example of a (small portion of) a
    weather dictionary:
        
        {
            "2017-04-21T08:00:00-04:00": {
                "visibility": {
                "prevailing": 10.0,
                "units": "SM"
            },
            "wind": {
                "speed": 13.0,
                "crosswind": 2.0,
                "units": "KT"
            },
            "temperature": {
                "value": 13.9,
                "units": "C"
            },
            "sky": [
                {
                    "cover": "clouds",
                    "type": "broken",
                    "height": 700.0,
                    "units": "FT"
                }
            ],
            "code": "201704211056Z"
        },
        "2017-04-21T07:00:00-04:00": {
            "visibility": {
                "prevailing": 10.0,
                "units": "SM"
            },
            "wind": {
                "speed": 13.0,
                "crosswind": 2.0,
                "units": "KT"
            },
            "temperature": {
                "value": 13.9,
                "units": "C"
            },
            "sky": [
                {
                    "type": "overcast",
                    "height": 700.0,
                    "units": "FT"
                }
            ],
            "code": "201704210956Z"
        }
        ...
    },
    
    If there is a report whose timestamp matches the ISO representation of takeoff, 
    this function uses that report.  Otherwise it searches the dictionary for the most
    recent report before (but not equal to) takeoff.  If there is no such report, it
    returns None.
    
    Example: If takeoff was as 8 am on April 21, 2017 (Eastern), this function returns 
    the value for key '2017-04-21T08:00:00-04:00'.  If there is no additional report at
    9 am, a 9 am takeoff would use this value as well.
    
    Parameter takeoff: The takeoff time
    Precondition: takeoff is a datetime object
    
    Paramater weather: The weather report dictionary 
    Precondition: weather is a dictionary formatted as described above
    """
    # Convert takeoff time to ISO string (matches the keys in weather)
    takeoff_iso = takeoff.isoformat()

    # First, check if there is an exact match for the takeoff time
    if takeoff_iso in weather:
        return weather[takeoff_iso]

    # If not, search for the most recent report before takeoff
    closest_time = None
    for key in weather:
        try:
            # Parse the key as a datetime object
            report_time = utils.str_to_time(key, takeoff.tzinfo)
            # Only consider reports before takeoff
            if report_time is not None and report_time < takeoff:
                # Update if this is the latest report before takeoff
                if closest_time is None or report_time > closest_time:
                    closest_time = report_time
                    closest_key = key
        except Exception:
            continue  # Skip keys that can't be parsed

    # Return the most recent report before takeoff, or None if not found
    if closest_time is not None:
        return weather[closest_key]
    else:
        return None


def get_weather_violation(weather,minimums):
    """
    Returns a string representing the type of weather violation (empty string if flight is ok)
    
    The weather reading is a dictionary with the keys: 'visibility', 'wind', and 'sky'.
    These correspond to a visibility, wind, and ceiling measurement, respectively. It
    may have other keys as well, but these can be ignored. For example, this is a possible 
    weather value:
        
        {
            "visibility": {
                "prevailing": 21120.0,
                "minimum": 1400.0,
                "maximum": 21120.0,
                "units": "FT"
            },
            "wind": {
                "speed": 12.0,
                "crosswind": 3.0,
                "gusts": 18.0,
                "units": "KT"
            },
            "temperature": {
                "value": -15.6,
                "units": "C"
            },
            "sky": [
                {
                    "cover": "clouds",
                    "type": "broken",
                    "height": 2100.0,
                    "units": "FT"
                }
            ],
            "weather": [
                "light snow"
            ]
        }
    
    The minimums is a list of the four minimums ceiling, visibility, and max windspeed,
    and max crosswind speed in that order.  Ceiling is in feet, visibility is in statute
    miles, max wind and cross wind speed are both in knots. For example, 
    [3000.0,10.0,20.0,8.0] is a potential minimums list.
    
    This function uses bad_visibility, bad_winds, and bad_ceiling as helpers. It returns
    'Visibility' if the only problem is bad visibility, 'Winds' if the only problem is 
    wind, and 'Ceiling' if the only problem is the ceiling.  If there are multiple
    problems, it returns 'Weather', It returns 'Unknown' if no weather reading is 
    available (e.g. weather is None).  Finally, it returns '' (the empty string) if 
    the weather is fine and there are no violations.
    
    Parameter weather: The weather measure
    Precondition: weather is dictionary containing a visibility, wind, and ceiling measurement,
    or None if no weather reading is available.
    
    Parameter minimums: The safety minimums for ceiling, visibility, wind, and crosswind
    Precondition: minimums is a list of four floats
    """
    #If no weather reading is available, return 'Unknown'
    if weather is None:
        return 'Unknown'

    #Unpack the minimums
    min_ceiling, min_visibility, max_wind, max_crosswind = minimums

    #Check each violation type
    vis = bad_visibility(weather.get('visibility'), min_visibility)
    wind = bad_winds(weather.get('wind'), max_wind, max_crosswind)
    ceil = bad_ceiling(weather.get('sky'), min_ceiling)

    #Count how many are True
    violations = [vis, wind, ceil]
    count = sum(1 for v in violations if v)

    #Return the appropriate string
    if count == 0:
        return ''
    if count > 1:
        return 'Weather'
    if vis:
        return 'Visibility'
    if wind:
        return 'Winds'
    if ceil:
        return 'Ceiling'


# FILES TO AUDIT
# Sunrise and sunset
DAYCYCLE = 'daycycle.json'
# Hourly weather observations
WEATHER  = 'weather.json'
# The list of insurance-mandated minimums
MINIMUMS = 'minimums.csv'
# The list of all registered students in the flight school
STUDENTS = 'students.csv'
# The list of all take-offs (and landings)
LESSONS  = 'lessons.csv'


def list_weather_violations(directory):
    """
    Returns the (annotated) list of flight reservations that violate weather minimums.
    
    This function reads the data files in the given directory (the data files are all
    identified by the constants defined above in this module).  It loops through the
    list of flight lessons (in lessons.csv), identifying those takeoffs for which
    get_weather_violation() is not the empty string.
    
    This function returns a list that contains a copy of each violating lesson, together 
    with the violation appended to the lesson.
    
    Example: Suppose that the lessons
        
        S00687  548QR  I061  2017-01-08T14:00:00-05:00  2017-01-08T16:00:00-05:00  VFR  Pattern
        S00758  548QR  I072  2017-01-08T09:00:00-05:00  2017-01-08T11:00:00-05:00  VFR  Pattern
        S00971  426JQ  I072  2017-01-12T13:00:00-05:00  2017-01-12T15:00:00-05:00  VFR  Pattern
    
    violate for reasons of 'Winds', 'Visibility', and 'Ceiling', respectively (and are the
    only violations).  Then this function will return the 2d list
        
        [[S00687, 548QR, I061, 2017-01-08T14:00:00-05:00, 2017-01-08T16:00:00-05:00, VFR, Pattern, Winds],
         [S00758, 548QR, I072, 2017-01-08T09:00:00-05:00, 2017-01-08T11:00:00-05:00, VFR, Pattern, Visibility],
         [S00971, 426JQ, I072, 2017-01-12T13:00:00-05:00, 2017-01-12T15:00:00-05:00, VFR, Pattern, Ceiling]]
    
    REMEMBER: VFR flights are subject to minimums with VMC in the row while IFR flights 
    are subject to minimums with IMC in the row.  The examples above are all VFR flights.
    If we changed the second lesson to
    
        S00758, 548QR, I072, 2017-01-08T09:00:00-05:00, 2017-01-08T11:00:00-05:00, IFR, Pattern
    
    then it is possible it is no longer a visibility violation because it is subject to
    a different set of minimums.
    
    Parameter directory: The directory of files to audit
    Precondition: directory is the name of a directory containing the files 'daycycle.json',
    'weather.json', 'minimums.csv', 'students.csv', and 'lessons.csv'
    """
    # Load all required files using the utils and pilots modules
    lessons = utils.read_csv(os.path.join(directory, LESSONS))
    students = utils.read_csv(os.path.join(directory, STUDENTS))
    minimums = utils.read_csv(os.path.join(directory, MINIMUMS))
    weather = utils.read_json(os.path.join(directory, WEATHER))
    daycycle = utils.read_json(os.path.join(directory, DAYCYCLE))  # Load daycycle.json for timezone and day/night

    # Prepare result list for violations
    violations = []

    # Iterate through each lesson (skip header row)
    for lesson in lessons[1:]:
        # Skip rows that do not have enough columns
        if len(lesson) < 7:
            continue

        # Extract relevant fields from the lesson row
        student_id = lesson[0]
        takeoff_str = lesson[3]
        filed = lesson[5]
        area = lesson[6]

        # Use utils.get_for_id to find the student row by id
        student_row = utils.get_for_id(student_id, students)
        if student_row is None:
            continue  # Skip if student not found

        # Parse takeoff time as datetime object (with timezone from daycycle)
        timezone = daycycle.get('timezone', 'UTC')
        takeoff = utils.str_to_time(takeoff_str, timezone)

        # Determine if an instructor is present (column 2 is instructor id)
        instructed = lesson[2] != ''

        # Use the FILED column to determine VFR/IFR for minimums (not pilot rating)
        # Normalize for case and whitespace
        vfr = (filed.strip().upper() == 'VFR')

        # Determine if the flight is during daytime using daycycle.json
        daytime = utils.daytime(takeoff, daycycle)

        # Get pilot certification at takeoff
        cert = pilots.get_certification(takeoff, student_row)

        # Get the minimums for this flight (may return None if no match)
        mins = pilots.get_minimums(cert, area, instructed, vfr, daytime, minimums)

        # Get the weather report at or before takeoff
        weather_report = get_weather_report(takeoff, weather)

        # Always check for a violation, even if mins is None
        violation = get_weather_violation(weather_report, mins)

        # If there is a violation, add a copy of the lesson with violation appended
        if violation is not None and violation != '':
            violations.append(lesson[:] + [violation])

    return violations

