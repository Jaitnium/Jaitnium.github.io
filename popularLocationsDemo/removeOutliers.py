import os
import sys
import json
import flickrapi
import math
from statistics import median

def calcDistance(lat1, lng1, lat2, lng2):
    return math.sqrt(pow(lat2 - lat1, 2) + pow(lng2 - lng1, 2))

def renameExistingFile(path, outputName, i):

    #Split into name + .json
    file = outputName.split(".")

    #Try to rename the old JSON file
    try:
    #print("Calling:")
    #print(path + "/" + outputName + "\nto\n" + path + "/" + file[0] + "_" + str(i) + "." + file[1])
        os.rename(path + "/" + outputName, path + "/" + file[0] + "_" + str(i) + "." + file[1])
    except OSError:
        #Try to rename with a higher index
        renameExistingFile(path, outputName, i + 1)

def getFlickrPlace(placeToFind):
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

    actualLat = placeFound['latitude']
    actualLng = placeFound['longitude']

    print("Actual lat + lng: " + actualLat + " " + actualLng)

    return (float(actualLat), float(actualLng))

#Removes the outliers from the given JSON file
def removeOutliers(path):
    print("Going to remove outliers from file " + path)
    with open(path) as data_file:
        #Determines removal threshold
        #Larger means less will be removed (if any)
        quartileMultipler = 2.0

        data = json.load(data_file)
        print("Total entries: " + str(len(data['photos']['photo'])))
        #for i in range(0, len(data.photos.photo))
        #Calculate the standard deviation for all the geolocations

        #Where the data will be stored
        #List of dictionaries will be added will be in the form: {lat, lng, dataIndex}
        #Any remaining data points after calculations will be returned
        retDictList = [];

        # First: Calculate the mean
        avgLat = 0; avgLng = 0;
        for i in range(0, len(data['photos']['photo'])):
            lat = float(data['photos']['photo'][i]['latitude'])
            lng = float(data['photos']['photo'][i]['longitude'])
            avgLat += lat
            avgLng += lng

            #Create an entry and add it to the array
            dictEntry = {'lat' : lat, 'lng' : lng, 'index' : i}
            retDictList.append(dictEntry)

        avgLat /= len(data['photos']['photo'])
        avgLng /= len(data['photos']['photo'])
        print("Avg lat + long: " + str(avgLat) + " " + str(avgLng))

        #Split path
        temp = path.split("/")
        #Get filename
        temp = temp[len(temp) - 1]
        #Get place from filename
        place = temp.split("_")[0]
        print(place)

        actualLatLng = getFlickrPlace(place)

        #Second : Calculate the distance between each point and the avgLat and avgLng
        for i in range(0, len(retDictList)):
            dist = calcDistance(retDictList[i]['lat'], retDictList[i]['lng'], actualLatLng[0], actualLatLng[1])
            #Add calculated dist to entry
            retDictList[i]['dist'] = dist

        #Sort retDictList by their dist value
        retDictList = sorted(retDictList, key=lambda k: k['dist'])

        #Calculate median
        #Array to hold dist values when calculating median
        tempArray = []
        for i in range(0, len(retDictList)):
            tempArray.append(retDictList[i]['dist'])

        quartile2 = median(tempArray)

        #Now, need to calculate Quartile1 and Quartile3
        #Create two arrays, one with all dist values lower than the medianVal
        #and another will all values greater than the median value
        lowerArray = []; higherArray=[];
        for i in range(0, len(tempArray)):
            #If lower, add to lower array
            if(tempArray[i] < quartile2):
                lowerArray.append(tempArray[i])
            else:
                higherArray.append(tempArray[i])
        quartile1 = median(lowerArray)
        print("quartile1: " + str(quartile1))
        print("quartile2: " + str(quartile2))
        quartile3 = median(higherArray)
        print("quartile3: " + str(quartile3))
        IQR = quartile3 - quartile1
        print("IQR: " + str(IQR))
        print("Quartile multipler: " + str(quartileMultipler))
        print("Removal threshold: " + str(quartile1 - quartileMultipler * IQR) + " " + str(quartile3 + quartileMultipler * IQR))

        #Now we have quartile1, 2, 3, and the IQR, which is enough to calculate outliers
        #Gowe're going to save the indicies of the data entries to remove
        amountRemoved = 0
        i = 0
        indiciesToPop = []
        for i in range(0, len(retDictList)):
            #If val <= Q1 - quartileMultipler *IQR
            if(retDictList[i]['dist'] <= quartile1 - quartileMultipler * IQR):
                #This is the index in the data dictionary to remove
                indiciesToPop.append(retDictList[i]['index'])
                amountRemoved += 1
            #Else If val >= Q3 + quartileMultipler * IQR
            elif(retDictList[i]['dist'] >= quartile3 + quartileMultipler * IQR):
                #This is the index in the data dictionary to remove
                indiciesToPop.append(retDictList[i]['index'])
                amountRemoved += 1

        print("Going to remove " + str(amountRemoved) + " entries..")

        #Now retDictList has its outliers removed
        #We can now get an array of the retDictList indicies to know which values to keep
        indiciesToPop = sorted(indiciesToPop)
        #for i in range(0, len(indiciesToPop)):
        #    print(indiciesToPop[i])

        #Change the "data" dictionary to reflect the removed elements
        #Traverse the the array backwards to bypass the problem of the array constantly shifting after popping indices
        #Start at the last index
        i = len(indiciesToPop) - 1;
        while i >= 0:
            data['photos']['photo'].pop(indiciesToPop[i])
            i -= 1
        print("new length: " + str(len(data['photos']['photo'])))

        #We're done! Data is updated and doesn't have any outliers
        #Write to a file and we're good as gravy

        temp = path.split("/")
        outputName = temp[len(temp) - 1]
        print("Going to create output file with new data into: " + outputName)
        #Dump into a JSON file named the same as this one
        with open(outputName, 'w') as outfile:
            json.dump(data, outfile, indent=4, sort_keys=True, separators=(',', ':'))

        print("Moving newly created file into the appropriate mapData directory and placing the old JSON file in this directory...")

        #Testing directory creation
        #Going to move
        #path = "./mapData"
        #Create if it doesn't exist
        #if not os.path.exists(path):
            #os.makedirs(path)
        #Check for year subdirectory
        #path = "./mapData/" + year
        #Create if it doesn't exist
         #if not os.path.exists(path):
            #os.makedirs(path)

        #Parse the name of the place from the returned filename
        #and create a folder with that name if it doesn't exist
        #placeName = fileName.split("_")[0]

        #Check for month subdirectory
        #path = "./mapData/" + placeName + "/" + year + "/" + month
        #Create if it doesn't exist
        #if not os.path.exists(path):
            #os.makedirs(path)

        #os.rename("mapData/San Francisco/2015/October/super test2.json", "mapData/San Francisco/2015/October/super test3.json")
        #print("mapData/San Francisco/2015/October/super test1.json")
        #print("mapData/San Francisco/2015/October/super test2.json")
        #os.rename("mapData/San Francisco/2015/October/San Francisco.json", "mapData/San Francisco/2015/October/San Francisco.json")
        #sys.exit()

    print("fileName: " + outputName)

    args = path.split("/")

    newPath = "mapData/" + args[1] + "/" + args[2] + "/" + args[3]
    #Create if it doesn't exist
    if not os.path.exists(newPath):
        print("Path doesn't exist, creating new path!")
        os.makedirs(newPath)

    #Call recursive helper to rename existing old file
    renameExistingFile(newPath, args[4], 1)

    #Move the newly created file to the correct directory
    try:
        os.rename(outputName, newPath + "/" + outputName)
    except OSError:
        #If the file exists, delete it and move the new file there
        print("File Exists: BUG, returning without moving the new file..")
        return
        os.remove(path + "/" + outputName)
        os.rename(outputName, path + "/" + outputName)

def printAllUsage():
    print("Usage: python removeOutliers.py [pathToJSON]")

if(sys.argv[1] == "-u" or sys.argv[1] == "-usage"):
    printAllUsage()
    sys.exit(0)

#Exit if not the correct number of arguments
if(len(sys.argv) != 2):
    printAllUsage()
    sys.exit(0)

#Call the remove outliers function and pass it the path to the JSON file
removeOutliers(sys.argv[1])