import flickrapi
import json
import sys
import datetime
import os
import textwrap

#"Month" and "Year" query flickr
#mintakenDate and maxtakenDate are created using the given month and year
#The JSON file is created using the given month and year
#Return the file's name that was created
def queryflickrMonth(placeToFind, month, year):

    #Create the mintakenDate and maxtakenDate given the month and year
    #Get the tuple
    dates = createTakenDates(month, year)
    mintakenDate = dates[0]
    maxtakenDate = dates[1]

    #Needed to access the API
    api_key = '082ca8bbb880bc514637527a4bfbe557'
    api_secret = 'c60206df6e5c1df1'

    #Create flickr handlers
    flickr = flickrapi.FlickrAPI(api_key, api_secret, format="parsed-json")
    flickrJSON = flickrapi.FlickrAPI(api_key, api_secret, format="json")

    #Fetch the location using the given string
    places = flickr.places.find(query=placeToFind)

    #If nothing was returned, signal error and exit
    if(len(places['places']['place'])) == 0:
        print("ERROR: Invalid 'placeToFind' string. flickr.places.find returned with an empty array. Exiting...")
        sys.exit(0)
    placeFound = places['places']['place'][0]

    #temp = textwrap.dedent(placeFound['_content']).encode(sys.getdefaultencoding())
    #print(type(placeFound['_content']))

    #print("Found place: " + temp + "which is of type: " + placeFound['place_type'])

    try:
        #Else, let the user know what was found and what we'll be getting data for
        print("Found place: " + placeFound['_content'] + " which is of type: " + placeFound['place_type'])
    except UnicodeEncodeError:
    	print("Found place can't be printed because it is in another language..")

    #Get the first page
    page = flickr.photos.search(place_id=placeFound['place_id'], has_geo="1", extras="geo", 
        per_page="250", page="1", min_taken_date=mintakenDate, max_taken_date=maxtakenDate)

    #Get the total number of pages to get
    numPages = page['photos']['pages']
    print(str(numPages) + " number of pages for " + month + " " + year)

    #Until we've fetched each page
    for i in range(2, numPages + 1):
        print("Appending page: " + str(i))
    	#Get the next page
        nextPage = flickr.photos.search(place_id=placeFound['place_id'], has_geo="1", extras="geo", 
        per_page="250", page=str(i), min_taken_date=mintakenDate, max_taken_date=maxtakenDate)

	    #Append the photo list to the first page
        page['photos']['photo'] = page['photos']['photo'] + nextPage['photos']['photo']


    print("Number of geolocations dumping to file: " + str(page['photos']['total']))

    #Correctly get the name of the place by parsing the first part of the returned '_content' field
    placeName = placeFound['_content'].split(",")[0]

    #Create the fileName based on the arguments
    outputName = placeName + "_" + month + "_" + year + ".json"

    print("Writing to file: " + outputName + " ...")

    #Dump into one json file using the name specified
    with open(outputName, 'w') as outfile:
	    json.dump(page, outfile, indent=4, sort_keys=True, separators=(',', ':'))

    return outputName

#"Raw" query flickr
def queryflickrRaw(placeToFind, mintakenDate, maxuptakenDate, outputName):

    api_key = '082ca8bbb880bc514637527a4bfbe557'
    api_secret = 'c60206df6e5c1df1'

    #Create flickr handlers
    flickr = flickrapi.FlickrAPI(api_key, api_secret, format="parsed-json")
    flickrJSON = flickrapi.FlickrAPI(api_key, api_secret, format="json")

    #Fetch the location using the given string
    places = flickr.places.find(query=placeToFind)
    print(len(places['places']['place']))

    #If nothing was returned, signal error and exit
    if(len(places['places']['place'])) == 0:
        print("ERROR: Invalid 'placeToFind' string. flickr.places.find returned with an empty array. Exiting...")
        sys.exit(0)
    placeFound = places['places']['place'][0]

    try:
        #Else, let the user know what was found and what we'll be getting data for
        print("Found place: " + placeFound['_content'] + "which is of type: " + placeFound['place_type'])
    except UnicodeEncodeError:
    	print("Found place can't be printed because it is in another language..")


    #Get the first page
    page = flickr.photos.search(place_id=placeFound['place_id'], has_geo="1", extras="geo", 
        per_page="250", page="1", min_taken_date=mintakenDate, max_taken_date=maxtakenDate)

    #Get the total number of pages to get
    numPages = page['photos']['pages']
    print(numPages)

    #Until we've fetched each page
    for i in range(2, numPages):
        print("Appending page: " + str(i))
    	#Get the next page
        nextPage = flickr.photos.search(place_id=placeFound['place_id'], has_geo="1", extras="geo", 
        per_page="250", page=str(i), min_taken_date=mintakenDate, max_taken_date=maxtakenDate)

	    #Append the photo list to the first page
        page['photos']['photo'] = page['photos']['photo'] + nextPage['photos']['photo']


    print("Number of geolocations dumping to file: " + str(len(page['photos']['photo'])))

    print("Writing to file: " + outputName + " ...")

    #Dump into one json file using the name specified
    with open(outputName + ".json", 'w') as outfile:
	    json.dump(page, outfile, indent=4, sort_keys=True, separators=(',', ':'))


def printRawUsage():
	#Raw dates
	print("To specify the exact date:\n python getflickrData.py -r [placeToFind] [mintaken date] [maxtaken date] [outputName].json")

def printMonthUsage():
	#Month
	print("To specify a month of a year:\n python getflickrData.py -m [placeToFind] [month] [year]")

def printYearUsage():
	#Full year
	print("To specify an entire year:\n python getflickrData.py -y [placeToFind] [year]")

#Print all usages
def printAllUsage():
    printRawUsage()
    printMonthUsage()
    printYearUsage()
    print("To force update index.json:\n python getflickrData.py -ui")

def verifyDate(datestring):
    try:
        datetime.datetime.strptime(datestring, '%Y-%m-%d')
        return
    except ValueError:
        print("ERROR: Invalid date string given: " + datestring + ". Exiting...")
        sys.exit(0)

def verifyYear(year):
    try:
        datetime.datetime.strptime(year, '%Y')
        return
    except ValueError:
        print("ERROR: Invalid year string given: " + year + ". Exiting...")
        sys.exit(0)

#Given a string for a month, check if valid
#Return the full name of the month
def verifyMonth(month):
    if(month == 'January' or month == 'Jan'):
    	return 'January'
    if(month == 'February' or month == 'Feb'):
    	return 'February'
    if(month == 'March' or month == 'Mar'):
    	return 'March'
    if(month == 'April' or month == 'April'):
    	return 'April'
    if(month == 'May' or month == 'May'):
    	return 'May'
    if(month == 'June' or month == 'June'):
    	return 'June'
    if(month == 'July' or month == 'July'):
    	return 'July'
    if(month == 'August' or month == 'Aug'):
    	return 'August'
    if(month == 'September' or month == 'Sep'):
    	return 'September'
    if(month == 'October' or month == 'Oct'):
    	return 'October'
    if(month == 'November' or month == 'Nov'):
    	return 'November'
    if(month == 'December' or month == 'Dec'):
    	return 'December'
    else:
        print("ERROR: Invalid month argument string: " + month + ". Exiting...")
        sys.exit(0)
 
 #Create the taken date strings and return as a tuple
def createTakenDates(month, year):

    if(month == 'January' or month == 'Jan'):
    	return (year + "-01-01", year + "-01-31")
    #Doesn't include leap year
    if(month == 'February' or month == 'Feb'):
    	return (year + "-02-01", year + "-02-28")
    if(month == 'March' or month == 'Mar'):
    	return (year + "-03-01", year + "-03-31")
    if(month == 'April' or month == 'April'):
    	return (year + "-04-01", year + "-04-30")
    if(month == 'May' or month == 'May'):
    	return (year + "-05-01", year + "-05-31")
    if(month == 'June' or month == 'June'):
    	return (year + "-06-01", year + "-06-30")
    if(month == 'July' or month == 'July'):
    	return (year + "-07-01", year + "-07-31")
    if(month == 'August' or month == 'Aug'):
    	return (year + "-08-01", year + "-08-31")
    if(month == 'September' or month == 'Sep'):
    	return (year + "-09-01", year + "-09-30")
    if(month == 'October' or month == 'Oct'):
    	return (year + "-10-01", year + "-10-31")
    if(month == 'November' or month == 'Nov'):
    	return (year + "-11-01", year + "-11-30")
    if(month == 'December' or month == 'Dec'):
    	return (year + "-12-01", year + "-12-31")
    else:
        print("ERROR: Invalid month: " + month + " year: " + year + "strings. How did we get here?! Exiting...")
        sys.exit(0)


#Verifies the argument flag
#Prints usage and exits if not valid
def verifyArguments(flag):
	#Print usage
    if(flag == '-usage'):
        printAllUsage()
        sys.exit(0)
    #Check arguments for "raw" usage
    if(flag == '-r'):
		#If not the correct number of args, print usage and exit
        if(len(sys.argv) != 6):
            printRawUsage()
            sys.exit(0)
		#Correct number of args, verify their validity
        else:
            #Check if dates are valid, exit if not
            #mintakenDate
            verifyDate(sys.argv[3])
            #maxtakenDate
            verifyDate(sys.argv[4])            

            #All "raw" arguments verified. Return
            return;
    #Check arguments for "month" usage
    if(flag == '-m'):
		#If not the correct number of args, print usage and exit
        if(len(sys.argv) != 5):
            printMonthUsage()
            sys.exit(0)
		#Correct number of args, verify their validity
        else:
            #Check if arguments are valid, exit if not
            #Month
            verifyMonth(sys.argv[3])
            print("Month verified!")
            #Year
            verifyYear(sys.argv[4])            
            print("Year verified!")
            #All "month" arguments verified. Return
            return;
    #Check arguments for "year" usage
    if(flag == '-y'):
		#If not the correct number of args, print usage and exit
        if(len(sys.argv) != 4):
            printYearUsage()
            sys.exit(0)
		#Correct number of args, verify their validity
        else:
            #Check if the year is valid, exit if not
            #Year
            verifyYear(sys.argv[3])            
            print("Year verified!")
            #All "year" arguments verified. Return
            return;
    #Check argument for "update index.json" usage
    if(flag == '-ui'):
        return;      
    #Any other arguments will cause the check to fail and exit
    else:
        printAllUsage()
        sys.exit(0)

#Create the JSON file corresponding to the arguments and place the file into the correct folder
#Create the corresponding folder hierarchy if it doesn't exist
def createMonthJSON(placeToFind, month, year):

    #Query flickr and the fileName that was created
    fileName = queryflickrMonth(placeToFind, month, year)

    #At this point we have a json file with all geo locations from placeToFind at month-year
    #Move the file called fileName to the appropriate folder, and create it if it doesn't exist

    #Testing directory creation
    path = "./mapData"
    #Create if it doesn't exist
    if not os.path.exists(path):
        os.makedirs(path)
    

    #Check for year subdirectory
    path = "./mapData/" + year
    #Create if it doesn't exist
    if not os.path.exists(path):
        os.makedirs(path)

    #Parse the name of the place from the returned filename
    #and create a folder with that name if it doesn't exist
    placeName = fileName.split("_")[0]

    #Check for month subdirectory
    path = "./mapData/" + placeName + "/" + year + "/" + month
    #Create if it doesn't exist
    if not os.path.exists(path):
        os.makedirs(path)

    print("fileName: " + fileName)
    #Move the newly created file to the correct directory
    try:
        os.rename(fileName, path + "/" + fileName)
    except OSError:
    	#If the file exists, delete it and move the new file there
        print("File Exists: Overwriting existing file..")
        os.remove(path + "/" + fileName)
        os.rename(fileName, path + "/" + fileName)

#This function creates a file called "index.json" with the folder structure of the given path
def createIndexJSON(path):
    d = {'name': os.path.basename(path)}
    if os.path.isdir(path):
        d['type'] = "directory"
        d['children'] = [createIndexJSON(os.path.join(path,x)) for x in os.listdir\
(path)]
    else:
        d['type'] = "file"
    return d

#MAIN START
#outfile is the name of the json file that contains the mapData structure
outfile = "index.json"
#Verify the arguments are valid
verifyArguments(sys.argv[1])

#If "raw" usage
if(sys.argv[1] == '-r'):
    placeToFind = sys.argv[2];
    mintakenDate = sys.argv[3];
    maxtakenDate = sys.argv[4];
    outputName = sys.argv[5];

    #Query flickr
    queryflickrRaw(placeToFind, mintakenDate, maxtakenDate, outputName)
    
    #Leave file in main folder
    sys.exit(0)

#If "month" usage
if(sys.argv[1] == '-m'):

    placeToFind = sys.argv[2];
    #VerifyMonth will return the full name of the month if an abbreviation is given
    month = verifyMonth(sys.argv[3])
    year = sys.argv[4]

    #Create the month's JSON, and place into the correct folder (creates it if it doesn't exist)
    createMonthJSON(placeToFind, month, year)

    #Create an index.json that reflects the changes
    with open(outfile, 'w') as outfile:
       json.dump(createIndexJSON('mapData'), outfile, indent=4, sort_keys=True, separators=(',', ':'))

#If "year" usage
if(sys.argv[1] == '-y'):
    placeToFind = sys.argv[2];
    year = sys.argv[3]

    #Create the JSON file for each month of the year
    #Creates any missing folders and places into those folders
    createMonthJSON(placeToFind, 'January', year)
    createMonthJSON(placeToFind, 'February', year)
    createMonthJSON(placeToFind, 'March', year)
    createMonthJSON(placeToFind, 'April', year)
    createMonthJSON(placeToFind, 'May', year)
    createMonthJSON(placeToFind, 'June', year)
    createMonthJSON(placeToFind, 'July', year)
    createMonthJSON(placeToFind, 'August', year)
    createMonthJSON(placeToFind, 'September', year)
    createMonthJSON(placeToFind, 'October', year)
    createMonthJSON(placeToFind, 'November', year)
    createMonthJSON(placeToFind, 'December', year)

    #Create an index.json that reflects the changes
    with open(outfile, 'w') as outfile:
       json.dump(createIndexJSON('mapData'), outfile, indent=4, sort_keys=True, separators=(',', ':'))

#If "update index.json" usage
if(sys.argv[1] == '-ui'):

    #Create an index.json that reflects the changes
    with open(outfile, 'w') as outfile:
       json.dump(createIndexJSON('mapData'), outfile, indent=4, sort_keys=True, separators=(',', ':'))

    print("index.json updated")    
