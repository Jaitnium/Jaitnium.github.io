import os
import sys
from shutil import copyfile
import json

def constructFilename(place, month, year):
	return place + "_" + month + "_" + year + ".json"

def getflickrData(args):

	print("\nRunning getflickrData.py...\n")

	call = 'python getflickrData.py '
	#Prepare getflickrData call
	for i in range(1, len(args)):
		call += args[i] + " "

	#The file will be placed into the appropriate mapData directory
	print(call)
	#Return status from program
	return os.system(call)

#Helper for createClusters
#Cnly performs createClusters.py on a single file
def createSingleCluster(place, month, year):

    fileName = constructFilename(place, month, year)

    #Testing directory creation
    path = "rawData"

    #Parse the name of the place from the returned filename
    #and create a folder with that name if it doesn't exist
    placeName = fileName.split("_")[0]

    #Create path argument for createClusters.py
    path = "rawData/" + placeName + "/" + year + "/" + month

    #Run the program with the file as the argument
    #The file will be placed in this file's directory
    os.system('python createClusters.py ' + path + "/" + fileName)

	#Create the corresponding mapData path
    #temp = path.split("/")
	#Replace "rawData" at the front of the path with "mapData"
    #mapDataPath = "mapData" + "/" + "/".join(temp[1:])

	#Create if it doesn't exist
    #if not os.path.exists(mapDataPath):
    #     os.makedirs(mapDataPath)

    #Move the newly created file to the correct directory
    #try:
    #    os.rename(fileName, mapDataPath + "/" + fileName)
    #except OSError:
        #If the file exists, delete it and move the new file there
    #    print("File Exists: Overwriting existing file..")
    #    os.remove(mapDataPath + "/" + fileName)
        #copyfile(fileName, path + "/" + fileName)
    #    os.rename(fileName, mapDataPath + "/" + fileName)

def createClusters(args):
	print("\nRunning createClusters.py...\n")

	if(args[1] == "-r"):
		print("Won't perform cluster on file created with flag '-r'")
		return
	if(args[1] == "-m"):
		createSingleCluster(args[2], args[3], args[4])
		return
	if(args[1] == "-y"):
		createSingleCluster(args[2], 'January', args[3])	
		createSingleCluster(args[2], 'February', args[3])	
		createSingleCluster(args[2], 'March', args[3])	
		createSingleCluster(args[2], 'April', args[3])	
		createSingleCluster(args[2], 'May', args[3])	
		createSingleCluster(args[2], 'June', args[3])	
		createSingleCluster(args[2], 'July', args[3])	
		createSingleCluster(args[2], 'August', args[3])	
		createSingleCluster(args[2], 'September', args[3])	
		createSingleCluster(args[2], 'October', args[3])	
		createSingleCluster(args[2], 'November', args[3])	
		createSingleCluster(args[2], 'December', args[3])	
		return

#Given a path in rawData
#Run all json files found through createClusters.py and create the corresponding folder structure in mapData
def clusterRecursiveAll(path):
	children = os.listdir(path)
	for i in range(0, len(children)):
		if(os.path.isdir(path + "/" + children[i])):
			clusterRecursiveAll(path + "/" + children[i])
		else:

			#Ensure this file is a .json file
			temp = children[i].split(".")
			if(temp[1] != "json"):
				print("Ignoring file " + children[i] + " because is not a json file")
				continue

			#We have a .json file to run through the cluster algorithm
			print("Creating cluster for file: " + children[i])
			filePath = path + "/" + children[i]
			#Enclose path in quotes in case of spaces
			os.system("python createClusters.py " + '"' + filePath + '"')
			print("")
			#The file will be output to this directory, so create the corresponding directory
			#structure under mapData and move the output file there

			#Create the corresponding mapData path
		#	temp = path.split("/")
			#Replace "rawData" at the front of the path with "mapData"
		#	mapDataPath = "mapData" + "/" + "/".join(temp[1:])
			#print("mapDataPath: ", end="")
			#print(mapDataPath)
			#Create if it doesn't exist
		#	if not os.path.exists(mapDataPath):
		#		os.makedirs(mapDataPath)

		#	fileName = children[i]
			#Move to the new directory
    		#Move the newly created file to the correct directory
		#	try:
		#		os.rename(fileName, mapDataPath + "/" + fileName)
		#	except OSError:
       		 #If the file exists, delete it and move the new file there
		#		print("File Exists: Overwriting existing file..")
		#		os.remove(mapDataPath + "/" + fileName)
		#		os.rename(fileName, mapDataPath + "/" + fileName)

#Given a path in rawData
#Run all json files found through createClusters.py and create the corresponding folder structure in mapData
def clusterRecursiveNew(path):
	children = os.listdir(path)
	for i in range(0, len(children)):
		if(os.path.isdir(path + "/" + children[i])):
			clusterRecursiveNew(path + "/" + children[i])
		else:

			#Ensure this file is a .json file
			temp = children[i].split(".")
			if(temp[1] != "json"):
				print("Ignoring file " + children[i] + " because is not a json file")
				continue

			#Create the corresponding mapData path
			temp = path.split("/")
			#Replace "rawData" at the front of the path with "mapData"
			mapDataPath = "mapData" + "/" + "/".join(temp[1:])
			#print("mapDataPath: ", end="")
			#print(mapDataPath)

			#If the file exists in mapData then it isn't new, skip this JSON file
			if os.path.exists(mapDataPath + "/" + children[i]):
				print("mapData file exists: " + mapDataPath + "/" + children[i])
				continue

			#We have a .json file to run through the cluster algorithm
			print("Creating cluster for file: " + children[i])
			filePath = path + "/" + children[i]
			#Enclose path in quotes in case of spaces
			os.system("python createClusters.py " + '"' + filePath + '"')
			print("")

			#Directory doesn't exist, so make it
		#	if not os.path.exists(mapDataPath):
		#		os.makedirs(mapDataPath)

			#The file will be output to this directory, so create the corresponding directory
			#structure under mapData and move the output file there

		#	fileName = children[i]
			#Move to the new directory
    		#Move the newly created file to the correct directory
		#	try:
		#		os.rename(fileName, mapDataPath + "/" + fileName)
		#	except OSError:
       		 #If the file exists, delete it and move the new file there
				#print("File Exists: Overwriting existing file..")
		#		os.remove(mapDataPath + "/" + fileName)
		#		os.rename(fileName, mapDataPath + "/" + fileName)

#Given the dictionary of entries retrieved from flickr
#Return the data without entries at exactly lat, lng: 0, 0
def removeGarbageEntries(data):
    i = 0
    e = 0
    print("Removing garbage entries...")
    while i < len(data['photos']['photo']):
        lat = data['photos']['photo'][i]['latitude']
        lng = data['photos']['photo'][i]['longitude']
        if(lat == 0 and lng == 0):
            e += 1
            data['photos']['photo'].pop(i)
        else:
            i += 1
    print("Removed " + str(e) + " garbage entries")

    return data

#Create a new .JSOn file with the data from the json files at path1 and path2
def appendFiles(path1, path2, fileName):
	data1 = {}
	data2 = {}

	with open(path1) as data_file:
		#Open JSOn file
		data = json.load(data_file)
		data1 = removeGarbageEntries(data)

	with open(path2) as data_file:
		#Open JSOn file
		data = json.load(data_file)
		data2 = removeGarbageEntries(data)

	print(len(data1['photos']['photo']))
	print(len(data2['photos']['photo']))
	data1['photos']['photo'] += data2['photos']['photo']
	print(len(data1['photos']['photo']))

	print("Writing to file: " + fileName + " ...")

    #Dump into one json file using the name specified
	with open(fileName + ".json", 'w') as outfile:
		json.dump(data1, outfile, indent=4, sort_keys=True, separators=(',', ':'))


def printDescription():
	print("This script will use the following programs: getflickrData.py and createClusters.py")
	print("getflickrData.py creates raw JSON files of photos retrieved from flickr")
	print("createClusters.py refines the raw JSON file into a smaller set of points and clusters the points.")

def printUsage():
	print("To run through ALL of the steps:\n python makeJSONFile.py -all [getflickrData arguments]")
	print("createClusters WON'T be performed on any getflickrData call with a -r flag")
	print("\nmakeJSONFile.py -ca [pathToCluster]")
	print("Given a path to a subdirectory of rawData, create the mapData counterpart JSON files and put them into mapData")
	print("\nmakeJSONFile.py -cn [pathToCluster]")
	print("Given a path to a subdirectory of rawData, only create the mapData counterparts IF they don't exist already")
	print("\nmakeJSONFile.py -append [pathInRawData] [pathInRawData] [fileName].json")
	print("Given two paths, create a JSON file with the combined marker points. Doesn't affect the original two files")

#MAIN
if(len(sys.argv) == 1 or sys.argv[1] == "-u" or sys.argv[1] == "-usage"):
	printDescription()
	print("")
	printUsage()
	sys.exit(0)

#Run through ALL steps
if(sys.argv[1] == "-all"):
	#Perform getflickrData.py
	ret = getflickrData(sys.argv[1:])

	#Perform createClusters.py if getflickrData.py didn't result in an error
	if(ret != 0):
		print("getflickrData exited with an error, not performing createClusters..")
		sys.exit(1)
	else:
		createClusters(sys.argv[1:])
		#Update index
		os.system("python getflickrData.py -ui")	
		sys.exit(0)

#Cluster everything
elif(sys.argv[1] == "-ca"):
	#So we can be given:
	#mapData/
	#mapData/PLACE/
	#mapData/PLACE/YEAR
	#mapData/PLACE/YEAR/MONTH

	if(len(sys.argv) < 3):
		printUsage()
		sys.exit(1)
	path = sys.argv[2]
	#Traverse all subdirectories of the given path
	#print(os.listdir(path))

	clusterRecursiveAll(path)
	#Update index
	os.system("python getflickrData.py -ui")
	#And then perform createClusters.py on each file, creating the corresponding mapData structure as we go

#Cluster new
elif(sys.argv[1] == "-cn"):
	if(len(sys.argv) < 3):
		printUsage()
		sys.exit(1)
	path = sys.argv[2]
	#Traverse all subdirectories of the given path
	#print(os.listdir(path))

	clusterRecursiveNew(path)
	#Update index
	os.system("python getflickrData.py -ui")
	#And then perform createClusters.py on each file, creating the corresponding mapData structure as we go

#Append two files
elif(sys.argv[1] == "-append"):
	if(len(sys.argv) != 5):
		printUsage()
		sys.exit(1)
	path1 = sys.argv[2]
	path2 = sys.argv[3]
	fileName = sys.argv[4]
	appendFiles(path1, path2, fileName)