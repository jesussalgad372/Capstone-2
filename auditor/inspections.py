"""
Module to check inspection violations for a flight lesson (OPTIONAL)

There are three kinds of inspection violations. (1) A plane has gone more than
a year since its annual inspection. (2) A plane has accrued 100 hours of flight
time since its last regular inspection. (3) A plane is used for a lesson despite
the repair logs claiming that it is in the shop for maintenance.

This module is MUCH more difficult than the others.  In the other modules, we
provided specifications for all of the helper functions, to make the main
function (listing all violations) easier.  We do not do that at all here.
You have one specification for one function.  Any additional functions (which
we do recommend) are up to you.

The other tricky part is keeping track of the hours since the last inspection
for each plane.  It is possible to do this with a nested loop, but the result
will be very slow (the application will take several minutes to complete).
To speed it up, you have to figure out how to "interleave" lessons with repairs.
This is a very advanced programming problem.

To implement this module, you need to familiarize yourself with two files
beyond what you have used already.

First of all, recall that fleet.csv is a CSV file with the following header:

    TAILNO  TYPE  CAPABILITY  ADVANCED  MULTIENGINE ANNUAL  HOURS

This lists the planes at the flight school.  For this module you need the
last two columns, which are strings representing a date and an number,
respectively.  The date is the last annual inspection for that plane as of
the beginning of the year (e.g. the start of the audit).  The number is
the number of hours since the last 100 hour inspection.

In addition, repairs.csv is a CSV file with the following header:

    TAILNO  IN-DATE  OUT-DATE  DESCRIPTION

The first column is the string identifying the plane.  The next two columns are
strings representing dates, for when the plane enters and leaves the shop (so
it should not fly during this time).  The last column is the type of repair.
A plane must be inspected/repaired every 100 hours.  In addition, it must have
an annual inspection once a year.  Other repairs happen as needed.  ANY repair
resets the number of hours on the plane.

The preconditions for many of these functions are quite messy.  While this
makes writing the functions simpler (because the preconditions ensure we have
less to worry about), enforcing these preconditions can be quite hard. That is
why it is not necessary to enforce any of the preconditions in this module.

Author: Jesus Salgado
Date: 6/28/2025
"""
import os.path
import datetime
import utils

# FILENAMES
# Sunrise and sunset (mainly useful for timezones, since repairs do not have them)
DAYCYCLE = 'daycycle.json'
# The list of all take-offs (and landings)
LESSONS  = 'lessons.csv'
# The list of all planes in the flight school
PLANES   = 'fleet.csv'
# The list of all repairs made to planes over the past year
REPAIRS  = 'repairs.csv'


def list_inspection_violations(directory):
    """
    Returns the (annotated) list of flight lessons that violate inspection
    or repair requirements.

    This function reads the data files in the given directory (the data files
    are all identified by the constants defined above in this module).  It loops
    through the list of flight lessons (in lessons.csv), identifying those
    takeoffs for which (1) a plane has gone MORE than a year since its annual
    inspection, (2) a plane has accrued OVER 100 hours of flight time since its
    last repair or inspection, and (3) a plane is used for a lesson despite
    the repair logs claiming that it is in the shop for maintenance.

    Note that a plane landing with exactly 100 hours used is not a violation.
    Nor is a plane that has flown with 365 days since its last inspection. This
    school likes to cut things close to safe money, but these are technically
    not violations.

    This function returns a list that contains a copy of each violating lesson,
    together with the violation appended to the lesson.  Violation of type (1)
    is annotated 'Annual'.  Violation of type (2) is annotated 'Inspection'.
    Violations of type (3) is annotated 'Grounded'.  If more than one is
    violated, it should be annotated 'Maintenance'.

    Example: Suppose that the lessons

        S00898  811AX  I072  2017-01-27T13:00:00-05:00  2017-01-27T15:00:00-05:00  VFR  Pattern
        S00681  684TM  I072  2017-02-26T14:00:00-05:00  2017-02-26T17:00:00-05:00  VFR  Practice Area
        S01031  738GG  I010  2017-03-19T13:00:00-04:00  2017-03-19T15:00:00-04:00  VFR  Pattern

    violate for reasons of 'Annual', 'Inspection', and 'Grounded', respectively
    (and are the only violations).  Then this function will return the 2d list

        [['S00898', '811AX', 'I072', '2017-01-27T13:00:00-05:00', '2017-01-27T15:00:00-05:00', 'VFR', 'Pattern', 'Annual'],
         ['S00681', '684TM', 'I072', '2017-02-26T14:00:00-05:00', '2017-02-26T17:00:00-05:00', 'VFR', 'Practice Area', 'Inspection'],
         ['S01031', '738GG', 'I010', '2017-03-19T13:00:00-04:00', '2017-03-19T15:00:00-04:00', 'VFR', 'Pattern', 'Grounded']]

    Parameter directory: The directory of files to audit
    Precondition: directory is the name of a directory containing the files
    'daycycle.json', 'fleet.csv', 'repairs.csv' and 'lessons.csv'
    """
    # Load data
    lessons = utils.read_csv(os.path.join(directory, LESSONS))[1:]  # skip header
    planes = utils.read_csv(os.path.join(directory, PLANES))[1:]
    repairs = utils.read_csv(os.path.join(directory, REPAIRS))[1:]

    daycycle = utils.read_json(os.path.join(directory, DAYCYCLE))
    timezone = daycycle.get('timezone', 'UTC')

    # Build initial state for each plane
    plane_state = {}
    for row in planes:
        tail = row[0]
        last_annual = utils.str_to_time(row[5], timezone)
        hours_since_100 = float(row[6]) if row[6] else 0.0
        plane_state[tail] = {
            'last_annual': last_annual,
            'hours_since_100': hours_since_100,
            'in_shop_periods': [],
            'repairs': []
        }
    # Add repairs to state
    for row in repairs:
        tail = row[0]
        in_date = utils.str_to_time(row[1], timezone)
        out_date = utils.str_to_time(row[2], timezone)
        desc = row[3].strip().lower()
        if tail in plane_state:
            if desc == 'annual inspection':
                plane_state[tail]['repairs'].append({'type': 'annual', 'date': in_date})
            else:
                plane_state[tail]['repairs'].append({'type': 'repair', 'date': in_date})
            plane_state[tail]['in_shop_periods'].append((in_date, out_date)) 

    # Build a timeline of all events (lessons and repairs) for each plane
    events = []
    for lesson in lessons:
        tail = lesson[1]
        takeoff = utils.str_to_time(lesson[3], timezone)   # <-- Pass timezone!
        landing = utils.str_to_time(lesson[4], timezone)   # <-- Pass timezone!
        events.append((tail, takeoff, 'lesson', lesson, landing))
    for tail, state in plane_state.items():
        for rep in state['repairs']:
            events.append((tail, rep['date'], rep['type'], None, None))
    events.sort(key=lambda x: (x[0], x[1]))

    # Track state for each plane as we process events
    current_annual = {tail: state['last_annual'] for tail, state in plane_state.items()}
    current_hours = {tail: state['hours_since_100'] for tail, state in plane_state.items()}
    last_landing = {tail: None for tail in plane_state}

    violations = []
    for event in events:
        tail, time, etype, lesson, landing = event
        if etype == 'lesson':
            # Check if plane is in shop during this lesson
            grounded = False
            for in_date, out_date in plane_state[tail]['in_shop_periods']:
                if (in_date is not None and out_date is not None and
                    ((time >= in_date and time < out_date) or (landing > in_date and landing <= out_date) or (time <= in_date and landing >= out_date))):
                    grounded = True
                    break
            # Check annual
            annual = False
            if current_annual[tail] is not None and (time - current_annual[tail]).days > 365:
                annual = True
            # Check 100-hour
            inspection = False
            duration = (landing - time).total_seconds() / 3600.0 if landing and time else 0.0
            # Flag if the plane starts at or above 100 hours, or crosses 100 hours during this flight
            if current_hours[tail] >= 100.0 or (current_hours[tail] < 100.0 and current_hours[tail] + duration > 100.0):
                inspection = True
            # Annotate
            annots = []
            if annual:
                annots.append('Annual')
            if inspection:
                annots.append('Inspection')
            if grounded:
                annots.append('Grounded')
            if len(annots) > 1:
                annotation = 'Maintenance'
            elif annots:
                annotation = annots[0]
            else:
                annotation = None
            if annotation:
                violations.append(lesson + [annotation])
            # Update state
            current_hours[tail] += duration
            last_landing[tail] = landing
        elif etype == 'annual':
            current_annual[tail] = time
            current_hours[tail] = 0.0
        elif etype == 'repair':
            current_hours[tail] = 0.0
    return violations