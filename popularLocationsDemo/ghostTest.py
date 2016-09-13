#Guide followed from jeanphix.me/Ghost.py

#Install PyQt
#So you can install Ghost
#pip install Ghost.py

import ghost
import sys
import json
from googleplaces import GooglePlaces, types, lang

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
	HSDict['entries'] = len(HSArray)
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
        result, resources = session.evaluate("getHotSpotJSON('2015', 'January', 'San Francisco', 15)")
        print(result)
        result, resources = session.wait_for_alert(100)
        #print(result)
        return result
        #results, resources = session.wait_for_text("Total")
        #results, resources = session.wait_for_selector("HSRet")
        #result, resources = session.wait_for_alert(timeout=30)
        #session.wait_for_page_loaded()
        #result, resources = session.evaluate("document.getElementById('HSRet').innerHTML");

#MAIN
#python ghostTest.py year month placeString zoom

#if(sys.argv[1] == "-usage" or sys.argv[1] == "-u"):
#	print("Usage: python ghostTest.py [year] [month] [place] [zoom]")
#	sys.exit()



def build_URL(lat, lng, radius):
    base_url = 'https://maps.googleapis.com/maps/api/place/nearbysearch/json?'
    location = 'location=' + lat + "," + lng
    radius = 'radius=' + radius
    key_string = '&key='+'082ca8bbb880bc514637527a4bfbe557'
    url = base_url+location+radius+key_string
    return url

#url = build_URL("37.80864212711866", "-122.47142523728814", "10")
#print(url)
#response = urlopen(url)
#print(response)

YOUR_API_KEY = 'AIzaSyCsWHtQAvGirxFXX6Ccmg6lkBj8Su80law'

google_places = GooglePlaces(YOUR_API_KEY)

query_result = google_places.nearby_search(lat_lng={'lat' : 37.81056165132787, 'lng' : -122.4105678498745}, radius=10)


for place in query_result.places:
    # Returned places from a query are place summaries.
    print(place.name)
    print("\n")
    print(place.geo_location)
    print("\n")
    print(place.place_id)
    print("\n")

    # The following method has to make a further API call.
    place.get_details()
    # Referencing any of the attributes below, prior to making a call to
    # get_details() will raise a googleplaces.GooglePlacesAttributeError.
    print(place.details) # A dict matching the JSON response from Google.
    print(place.local_phone_number)
    print(place.international_phone_number)
    print(place.website)
    print(place.url)

    # Getting place photos

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

outputName = "HS" + "_" + place + "_" + month + "_" + year + ".json"

print("Writing data to " + outputName + " ...")

#Dump into one json file using the name specified
with open(outputName, 'w') as outfile:
   json.dump(HSDict, outfile, indent=4, sort_keys=True, separators=(',', ':'))

print("Done!")
sys.exit()   