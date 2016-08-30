#Guide followed from jeanphix.me/Ghost.py

#Install PyQt
#So you can install Ghost
#pip install Ghost.py

import ghost
import sys
import json

#Given the raw output from the webpage
#Return a dictionary of the lat/long data
def rawToJSON(raw, year, month, place, zoom):
	#split the raw data into an array of entries
	entries = raw.split("\n")
	#print(raw.split("\n"))
	#dictionary to add all points
	HSDict = {}
	#contains array of tuples: {lat, lng}
	HSArray = []

	#For each entry
	for i in range(0, len(entries) - 1):
	#for i in range(0, 9):

		#Split the entry into three numbers: the index, lat, and lng
		entry = entries[i].split(" ")
		lat = entry[1]
		lng = entry[2]
		#print(lat + " " + lng)
		#print(type(lat))
		#HSArray['lat'] = lat
		#HSArray['lng'] = lng

		HSArray.append({"lat" : lat, "lng" : lng})

	HSDict['year'] = year
	HSDict['month'] = month
	HSDict['place'] = place
	HSDict['zoom'] = zoom
	HSDict['array'] = HSArray

	print(HSDict)

	return HSDict

#Given a year, month, place, and zoom level
#Return the response from MatthewAntosiak.com's getHotSpotJSON function
def getRawData(year, month, place, zoom):
    g = ghost.Ghost()
    with g.start() as session:
        #page, extra_resources = session.open("https://jaitnium.github.io/popularLocationsDemo/flickrTest.html")
        #result, resources = session.evaluate("document.getElementById('displayBtn').innerHTML;");
        #print(result)
        #sys.exit()
        page, extra_resources = session.open("https://jaitnium.github.io/popularLocationsDemo/flickrTest.html")
        result, resources = session.evaluate("getHotSpotJSON('2015', 'January', 'Sanfrancisco', 17)")
        print(result)
        result, resources = session.wait_for_alert()
        #print(result)
        return result
        #results, resources = session.wait_for_text("Total")
        #results, resources = session.wait_for_selector("HSRet")
        #result, resources = session.wait_for_alert(timeout=30)
        #session.wait_for_page_loaded()
        #result, resources = session.evaluate("document.getElementById('HSRet').innerHTML");

#MAIN
#python ghostTest.py year month placeString zoom

if(sys.argv[1] == "-usage" or sys.argv[1] == "-u"):
	print("Usage: python ghostTest.py [year] [month] [place] [zoom]")
	sys.exit()

year = sys.argv[1]
month = sys.argv[2]
place = sys.argv[3]
zoom = sys.argv[4]

print("Attempting to retrieve data from website with year=" + year + ", month=" + month + ", place="
	+ place + ", zoom=" + zoom)

#Where the raw output from the webpage is stored
rawHSData = getRawData(year, month, place, zoom)

#print(rawHSData)
print("Retrieved data.. converting to dictionary")

HSDict = rawToJSON(rawHSData, year, month, place, zoom)

outputName = place + "_" + month + "_" + year + "_" + "HS.json"

print("Writing data to " + outputName + " ...")

#Dump into one json file using the name specified
with open(outputName, 'w') as outfile:
   json.dump(HSDict, outfile, indent=4, sort_keys=True, separators=(',', ':'))

print("Done!")
sys.exit()   