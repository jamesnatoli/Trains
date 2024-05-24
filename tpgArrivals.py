#!/usr/local/bin/python3 
########### Python 3.7 #############
import time
import sys

import requests
from bs4 import BeautifulSoup as bs

from datetime import datetime, timedelta
from dateutil.tz import tzutc, tzlocal

import argparse

# 8587918 (CERN)
# 1401791 (SGP-Lion)

stationDict = {
    "cern"              : 8587918,
    "saint-genis, lion" : 1401791,
    "sgl"               : 1401791,
}

parser = argparse.ArgumentParser( description='Display tram/bus times for the TPG Network')
parser.add_argument( '-s', '--station', dest='stationOfInterest', action="store" , required=False, default='CERN',
                     help='Station of Interest', type=str)
parser.add_argument( '-r', '--run', dest='run', action="store_true" , required=False, default=False,
                     help='Run continuously every 30 sec [BROKEN]')
parser.add_argument( '-l', '--line', dest='line', action="store", required=False, default=None,
                     help='Only show information about a specific line')
parser.add_argument( '-j', '--justNext', dest='justNext', action="store_true", required=False, default=False,
                     help='Just display next arriving bus')
parser.add_argument( '-n', '--howMany', dest='howMany', action="store", required=False, default=3,
                     help='Set how many results to show (machine limited to max of 40)')
parser.add_argument( '-d', '--dump', dest='dump', action="store_true", required=False, default=False,
                     help='Dump xml content')

# TODO: add future time option?
# TODO: add more stations?

# Request headers
# move this somewhere else lol, should be private
headers = {
    'Authorization': 'eyJvcmciOiI2NDA2NTFhNTIyZmEwNTAwMDEyOWJiZTEiLCJpZCI6IjkyZjg1ZWQxZGVlYzQ1YTI5YzQxMTBmZTRkM2M4MDQ2IiwiaCI6Im11cm11cjEyOCJ9',
    'Content-Type': 'application/xml'
}

def reqConnect( args):
    numReqs = 1 if args.justNext else args.howMany
    
    # This one is more complex, has realtime data
    # link = 'https://api.opentransportdata.swiss/gtfsrt2020'
    link = 'https://api.opentransportdata.swiss/trias2020'
    
    # where the xml request is stored
    filename = '/Users/jamesnatoli/Documents/Programs/TPG/trias-xsd-v1.1/test.xsd'

    # Open the xml request file
    data = ""
    with open( filename, 'r') as f:
        data = f.read()

    # Safety Belts on
    if data == "":
        print("File error :(")
        exit(1)

    try:
        stationCode = stationDict[args.stationOfInterest.lower()]
    except KeyError as e:
        print("Error: Unknown Station")
        print("Please enter one of the following stations (case insensitive):")
        for station, code in stationDict.items():
            print( station)
        exit(1)

    body = ""
    timeCode = "%Y-%m-%dT%H:%M:%S%z"
    currTime = datetime.now( tzlocal()).strftime( timeCode)
    for line in data.split('\n'):
        # Add the current time to the request
        if "DepArrTime" in line:
            timeString = "<DepArrTime>" + currTime + "</DepArrTime>"
            body += timeString
        # Change the number of results
        elif ("NumberOfResults" in line):
            if not args.line:
                numResultsString = "<NumberOfResults>" + str(numReqs) + "</NumberOfResults>"
            else:
                numResultsString = ""
            body += numResultsString
        # Change station
        elif "StopPointRef" in line:
            numResultsString = "<StopPointRef>" + str(stationCode) + "</StopPointRef>"
            body += numResultsString
        else:
            body += line

    # Get the request!
    r = requests.post( link, data=body, headers=headers)

    # lxml keeps giving XMLParsedAsHTMLWarning 
    # bs_data = bs( r.content, "lxml")
    bs_data = bs( r.content, 'xml')
    if (args.dump): print( f"BS Data: \n{bs_data.prettify()}")

    stopEvents = bs_data.find_all("StopEventResult")

    counter = 1
    print( f"Displaying results for stop: {args.stationOfInterest}")
    for i, stopEvent in enumerate(stopEvents):        
        # Check line num in case we're skipping
        lineNumber = stopEvent.find("PublishedLineName").find("Text").text
        if ((counter > int(args.howMany)) or ((args.line is not None) and (args.line != lineNumber))):
            continue

        print( f"\n*** Stop: {i+1} ***")
        counter += 1
            
        destName   = stopEvent.find("DestinationText").find("Text").text
        timetabledTime = stopEvent.find("TimetabledTime").text
        transitMode = stopEvent.find("PtMode").text
        print( f"Line Number   : {lineNumber}")
        print( f"Destination   : {destName}")

        # Time Stuff
        timetableVar = datetime.strptime( timetabledTime, timeCode).astimezone( tzlocal())
        currTimeVar = datetime.now( tzlocal())
        leavingIn = int((timetableVar - currTimeVar).total_seconds() / 60)
        print( f"Timetable Time: {timetableVar}")
        if stopEvent.find("EstimatedTime"):
            estTime = stopEvent.find('EstimatedTime').text
            estVar = datetime.strptime( estTime, timeCode).astimezone( tzlocal())
            print( f"Estimated Time: {estVar}")

            # Late or Early
            diffTime = int((estVar - timetableVar).total_seconds() / 60)
            leavingIn = int((estVar - currTimeVar).total_seconds() / 60)
            if diffTime != 0:
                # Late
                if diffTime > 0:
                    if (diffTime > 1):
                        print(f"This {transitMode} is {diffTime} minutes late, leaving in {leavingIn} minute(s)!")
                    else:
                        print(f"This {transitMode} is {diffTime} minute late, leaving in {leavingIn} minute(s)!")
                # Early
                else:
                    if (abs(diffTime) > 1):
                        print(f"This {transitMode} is {abs(diffTime)} minutes early, leaving in {leavingIn} minute(s)!")
                    else:
                        print(f"This {transitMode} is {abs(diffTime)} minute early, leaving in {leavingIn} minute(s)!")
            else:
                print(f"This {transitMode} is on time, leaving in {leavingIn} minute(s) :)")
        else:
            print( "No Estimated time :(")
        
def main():
    args = parser.parse_args()

    reqConnect( args)
    
    
if __name__ == "__main__":
    try:
        main()
    except OSError as e:
        print("There was an error :(")
        print(f"[Errno {e.errno}] {e.strerror}")
    except KeyboardInterrupt as e:
        print("You've interrupted me :(")


        
