import sys
import json
import math
import os
#Given the path a JSON file, creates another JSON file of clusters

def printAllUsage():
    print("Usage: python createClusters.py [pathToJSON]")

#Given the JSON file data
#Return the topleft-most bound lat lng
#Takes into account quadrants
def getTopLeftGridBound(data):


	left = float(data['photos']['photo'][0]['longitude'])
	top = float(data['photos']['photo'][0]['latitude'])

	#Go through all points
	for i in range(0, len(data['photos']['photo'])):

		#If a point more west was found
		lng = float(data['photos']['photo'][i]['longitude'])
		lat = float(data['photos']['photo'][i]['latitude'])

		if lng < left:
			left = float(data['photos']['photo'][i]['longitude'])				

		if lat > top:
			top = float(data['photos']['photo'][i]['latitude'])				

	return [top, left]

#Given the JSON file data
#Return the botright-most bound lat lng
def getBotRightGridBound(data):

	right = float(data['photos']['photo'][0]['longitude'])
	bot = float(data['photos']['photo'][0]['latitude'])

	#Go through all points
	for i in range(0, len(data['photos']['photo'])):

		#If a point more west was found
		lng = float(data['photos']['photo'][i]['longitude'])
		lat = float(data['photos']['photo'][i]['latitude'])

		if lng > right:
			right = float(data['photos']['photo'][i]['longitude'])				

		if lat < bot:
			bot = float(data['photos']['photo'][i]['latitude'])				

	return [bot, right]

#Given the data from a JSON file
#Return the topLeft and botRight lat lng grid bound
def getGridBounds(data):
	topLeft = getTopLeftGridBound(data)
	print("topLeft: ", end="")
	print(topLeft)
	botRight = getBotRightGridBound(data)
	print("botRight: ", end="")
	print(botRight)
	return [topLeft, botRight]	


#Given the grid bounds, the element's index in the grid, and m
#Return the element's bounds
def getElementBounds(topLeft, botRight, i, j, m):
	#Calculate the vertical length of the grid
	#Difference between the latitudes
	gridVerticalLength = abs(float(topLeft[0]) - float(botRight[0]))
	#Calculate the horizontal length of the grid
	#Difference between the longitudes
	gridHorizontalLength = abs(float(topLeft[1]) - float(botRight[1]))

	horIndexBy = gridHorizontalLength/m
	vertIndexBy = gridVerticalLength/m

	#WARNING
	#THIS CODE WILL LIKELY BREAK ON ANOTHER LAT LNG QUADRANT

	#Index i times from the grid's left bound
	left = float(topLeft[1]) + i * horIndexBy
	#Index j times from the grid's top bound
	top = float(topLeft[0]) - j * vertIndexBy

	#Create element bounds
	topLeft = [top, left]
	botRight = [top - vertIndexBy, left + horIndexBy]

	return [topLeft, botRight]

#Given a grid sq and a lat,lng
#Return true if the lat,lng is within the sq, else false
def withinSquare(sq, point):
	#print(sq['topLeftBound'][0])
	#print(str(sq['topLeftBound'][0]) + " >= " + str(point['latitude']) + " >= " + str(sq['botRightBound'][0]))
	if(sq['topLeftBound'][0] >= float(point['latitude']) and float(point['latitude']) >= sq['botRightBound'][0]):
		#print(str(sq['topLeftBound'][1]) + " >= " + str(point['longitude']) + " >= " + str(sq['botRightBound'][1]))
		if(sq['topLeftBound'][1] <= float(point['longitude']) and float(point['longitude']) <= sq['botRightBound'][1]):
			return True
	return False

#Find the index of the square where the point belongs
def findSquare(squares, point):
	i = 0
	j = 0
	pntLng = float(point['longitude'])

	#Increment i until the point is within the square's lng bounds
	while i < len(squares):
		if( not (squares[i][j]['topLeftBound'][1] <= pntLng and pntLng <= squares[i][j]['botRightBound'][1])):
			i += 1
		else:
			break

	#Do a check to see if i wasn't found
	#In other words, the marker couldn't find a square because of a rounding error
	#So do a check on the spaces inbetween each sq's bounds
	if i == len(squares):
		i = 0
		while i < len(squares):
			if( not (pntLng <= squares[i][j]['botRightBound'][1])):
				i += 1
			else:
				print("Found an x square for missing point")
				break
		#If STILL reached the end, then it's just after the last sq
		if i == len(squares):
			i = len(squares) - 1

	pntLat = float(point['latitude'])

	#Increment j until the point is within the square's lat bounds
	while j < len(squares[i]):
		if( not (squares[i][j]['topLeftBound'][0] >= pntLat and pntLat >= squares[i][j]['botRightBound'][0])):
			j += 1
		else:
			break

	#Do a check to see if j wasn't found
	#In other words, the marker couldn't find a square because of a rounding error
	#So do a check on the spaces inbetween each sq's bounds
	if j == len(squares):
		j = 0
		while j < len(squares):
			if( not (pntLat >= squares[i][j]['botRightBound'][0])):
				j += 1
			else:
				print("Found an y square for missing point")
				break
		#If STILL reached the end, then it's just after the last sq
		if j == len(squares):
			j = len(squares) - 1

	return [i, j]

#Given the JSON file data and a grid
#Update each grid sq's density field to be the number of markers within it's bounds
def setDensities(data, grid) :
	points = data['photos']['photo']
	squares = grid['elements']

	print("Total points: " + str(len(points)))

	#For each point
	for i in range(0, len(points)):
		point = points[i]
		index = findSquare(squares, point)
		squares[index[0]][index[1]]['density'] += 1
		pair = [float(point['latitude']), float(point['longitude'])]
		squares[index[0]][index[1]]['points'].append(pair)

	#Remove squares without any density
	#for i in range(0, len(squares)):
	#	j = 0
	#	while j < len(squares[i]):
	#		if(squares[i][j]['density'] == 0):
	#			squares[i].pop(j)
	#		else:
	#			j += 1			

	#Set each sq's weighted point
	for i in range(0, len(squares)):
		for j in range(0, len(squares[i])):

			if(squares[i][j]['density'] == 0):
				continue

			points = squares[i][j]['points']

			latTot = 0
			lngTot = 0
			for k in range(0, len(points)):
				latTot += points[k][0]
				lngTot += points[k][1] 

			#Set the weighted point to be the average of its lat and lngs
			squares[i][j]['weightedPoint'] = [latTot/len(points), lngTot/len(points)]

	densityTotal = 0
	#Tally densities to make sure the code works
	for i in range(0, len(squares)):
		for j in range(0, len(squares[i])):
			densityTotal += squares[i][j]['density']


	print("densityTotal: " + str(densityTotal))
	return squares

def printTotalSquares(squares):
	total = 0
	for i in range(0, len(squares)):
		for j in range(0, len(squares[i])):
			if(squares[i][j]['density'] != 0):
				total += 1
	print("Total grid squares after removing empty ones: " + str(total))
	return total

def removePointsAttribute(grid):
	for i in range(0, len(grid['elements'])):
		for j in range(0, len(grid['elements'][i])):
			grid['elements'][i][j].pop('points', None)
	return grid
				
#Returns a grid Dictionary object structured as:
#topLeftBound
#botRightBound
#markerTotal:
#m:
#totalGridElements:
#gridElementArray:
#	{index:
#	 density (number of markers in bounds):
#	topLeftBound:
#	botRightBound:}
def createGrid(topLeft, botRight, m):
	grid = {}
	grid['topLeftBound'] = topLeft
	grid['botRightBound'] = botRight
	grid['m'] = m
	grid['totalGridElements'] = m * m
	grid['elements'] = [[{} for x in range(m)] for y in range(m)]
	for i in range(0, m):
		for j in range(0, m):
			#Create the element bounds
			elementGridBounds = getElementBounds(topLeft, botRight, i, j, m) 

			grid['elements'][i][j]['topLeftBound'] = elementGridBounds[0]
			grid['elements'][i][j]['botRightBound'] = elementGridBounds[1]
			grid['elements'][i][j]['density'] = 0
			grid['elements'][i][j]['points'] = []
			grid['elements'][i][j]['weightedPoint'] = []
			grid['elements'][i][j]['index'] = [i, j]
			grid['elements'][i][j]['clustered'] = False

	return grid

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

#Given a square's index
#Return an array of the element's unclustered neighbors
def getNeighbors(i, j, squares2D):
	neighbors = []

	#print("Trying to find neighbor for index: " + str(i) + " " + str(j))

	#print("Actual index: " + str(lookUp[0]) + " " + str(lookUp[1]))

	try:
		neighbors.append(squares2D[i - 1][j - 1])
	except IndexError:
		pass

	try:
		neighbors.append(squares2D[i - 1][j])
	except IndexError:
		pass

	try:
		neighbors.append(squares2D[i - 1][j + 1])
	except IndexError:
		pass

	try:
		neighbors.append(squares2D[i][j - 1])
	except IndexError:
		pass

	try:
		neighbors.append(squares2D[i][j + 1])
	except IndexError:
		pass

	try:
		neighbors.append(squares2D[i + 1][j - 1])
	except IndexError:
		pass

	try:
		neighbors.append(squares2D[i + 1][j])
	except IndexError:
		pass

	try:
		neighbors.append(squares2D[i + 1][j + 1])
	except IndexError:
		pass

	#Remove all neighbors that are clustered already or have a density of 0
	i = 0
	while i < len(neighbors):
		if(neighbors[i]['clustered'] == True or neighbors[i]['density'] == 0):
			neighbors.pop(i)
		else:
			i += 1		

	return neighbors

#Helper for clusterNieghbors
#The neighbors check their neighbors to see if there are clusters within the original's value
def neighborsCheck(neighbor, squares2D, originalDensity):
	#Get unclustered neighbors
	neighbors = getNeighbors(neighbor['index'][0], neighbor['index'][1], squares2D)
	#Add more neighbors within originalDensity's threshold here
	#Will be added to original cluster after returning
	cluster = []

	#For each neighbor
	for i in range(0, len(neighbors)):
		if(neighbors[i]['density'] >= originalDensity * 0.7):
			cluster.append(neighbors[i])
			#Update local grid copy to show neighbor is clustered for recursive call
			squares2D[neighbors[i]['index'][0]][neighbors[i]['index'][1]]['clustered'] = True
			#Check this neighbor's neighbors
			ret = neighborsCheck(neighbors[i], squares2D, originalDensity)
			cluster += ret

	return cluster

#Helper function
#Given the index i, j of a grid element, and the grid elements
#Return a pair [x, y] of the matching element with and index i, j
#Because the empty grid elements are thrown out, the indicies each element has isn't its real
#Location in the grid. Updating the indicies would make the grid elements all seem like neighbors
#(which they aren't)
def squareLookUp(x, y, squares2D):
	for i in range(0, len(squares2D)):
		for j in range(0, len(squares2D[i])):
			square = squares2D[i][j]
			if(square['index'][0] == x and square['index'][1] == y):
				return [i, j]

def clusterNeighbors(squares1D, squares2D):
	print("In cluster Neighbors")
	#print("\n2Darray: ", end="")
	#print(squares2D)
	#Clusters ia an array of cluster
	clusters = []
	#For each square
	for i in range(0, len(squares1D)):
		#A cluster is dictionary of a weighted average and an array of squares
		clusterArray = []

		#If this square has nothing in it
		if(squares1D[i]['density'] == 0):
			continue

		#If the square is clustered continue to the next square
		if(squares2D[squares1D[i]['index'][0]][squares1D[i]['index'][1]]['clustered'] == True):
			continue

		#Else set to clustered
		squares2D[squares1D[i]['index'][0]][squares1D[i]['index'][1]]['clustered'] = True
		#Add the square to a new cluster
		clusterArray.append(squares1D[i])
		#Get all neighbors to this square
		neighbors = getNeighbors(squares1D[i]['index'][0], squares1D[i]['index'][1], squares2D)

		#Just add to clusters if no neighbors
		if(len(neighbors) == 0):

			cluster = {}
			cluster['elements'] = clusterArray

			clusters.append(cluster)
		else:
			#Neighbors added to the cluster will also check their neighbors, but only AFTER all of these neighbors are processed
			neighborsToCheck = []
			#For each neighbor
			for j in range(0, len(neighbors)):
				#If the neighbor is within the threshold of the original
				if(neighbors[j]['density'] >= 0.7 * squares1D[i]['density']):
					#Updage the neighbor to clustered and add it to the cluster
					#lookUp = squareLookUp(neighbors[j]['index'][0], neighbors[j]['index'][1], squares2D)
					squares2D[neighbors[j]['index'][0]][neighbors[j]['index'][1]]['clustered'] = True
					clusterArray.append(neighbors[j])
					#Add to checkarray
					neighborsToCheck.append(neighbors[j])
			#Neighbor's neighbors to add
			moreToAdd = []
			for j in range(0, len(neighborsToCheck)):
				#Recursively check the neighbor
				ret = neighborsCheck(neighborsToCheck[j], squares2D, squares1D[i]['density'])
				#Add whatever was found
				moreToAdd = moreToAdd + ret
			#Go through each new square and update the grid to reflect that it is now "clustered"
			for j in range(0, len(moreToAdd)):
				#print(moreToAdd)
				#print(moreToAdd[j])
				#lookUp = squareLookUp(moreToAdd[j]['index'][0], moreToAdd[j]['index'][1], squares2D)
				squares2D[moreToAdd[j]['index'][0]][moreToAdd[j]['index'][1]]['clustered'] = True

			#Append if not empty
			if moreToAdd:
				#Add the neighbor's neighbors to the cluster
				#cluster.append(moreToAdd)
				clusterArray += moreToAdd
			#Finally Aad the cluster to clusters

			cluster = {}
			cluster['elements'] = clusterArray
			clusters.append(cluster)

	return clusters

#Sort the 2D array into a 1D sorted array by descending density
#and return the clusters
def getClusters(squares2D):
	squares1D = []
	#Add all squares to 1D array
	for i in range(0, len(squares2D)):
		for j in range(0, len(squares2D[i])):
			squares1D.append(squares2D[i][j])

	squares1D = sorted(squares1D, key=lambda k: k['density'], reverse=True)

	#Group the grid elements together with their neighbors
	clusters = clusterNeighbors(squares1D, squares2D)
	print("Number of clusters: " + str(len(clusters)))
	return clusters
	#for i in range(0, len(clusters)):
	#	print("cluster " + (str(i)), end="")
	#	print(clusters[i])

def createFakeClusters():
	m = 5
	squares = [[{} for x in range(m)] for y in range(m)]
	for i in range(0, len(squares)):
		for j in range(0, len(squares[i])):
			squares[i][j]['density'] = 0
			squares[i][j]['clustered'] = False
			squares[i][j]['index'] = [i, j]


	squares[3][3]['density'] = 100
	squares[3][2]['density'] = 70
	squares[3][1]['density'] = 71
	squares[2][3]['density'] = 81
	squares[1][1]['density'] = 80
	squares[4][1]['density'] = 72
	squares[4][4]['density'] = 95
	squares[3][4]['density'] = 69

	#Remove squares without any density
	#for i in range(0, len(squares)):
	#	j = 0
	#	while j < len(squares[i]):
	#		if(squares[i][j]['density'] == 0):
	#			squares[i].pop(j)
	#		else:
	#			j += 1			

	return squares

def createClusters(path):
	print("Going to create clusters of the file at " + path)

	temp = path.split("/")
	fileName = temp[len(temp) - 1]
	print("Cluster fileName: " + fileName)

	with open(path) as data_file:
		m = 2000
		#Open JSOn file
		data = json.load(data_file)
		#Remove any bad points
		#This probably shouldn't be done here in the future, should be done ahead of time
		data = removeGarbageEntries(data)

        #Step1: Create Grid
		print("Creating grid with m=" + str(m))
		gridBounds = getGridBounds(data)
		grid = createGrid(gridBounds[0], gridBounds[1], m)
		grid['totalPoints'] = len(data['photos']['photo'])

		#Step 2: Set density of each grid sq and set weighted geolocations for each sq
		squares = setDensities(data, grid)
		#squares = createFakeClusters()
		grid['elements'] = squares

		total = printTotalSquares(squares)
		grid['totalGridElements'] = total

		#Remove the points element from each sq
		grid = removePointsAttribute(grid)

		#Step 3: Sort elements in order of descending density
		clusters = getClusters(grid['elements'])
		grid['clusters'] = clusters

		#Step 3.5: Set weighted points for each cluster
		for i in range(0, len(grid['clusters'])):
			clusterArray = grid['clusters'][i]['elements']

			weightedX = 0
			weightedY = 0

			#Add the weighted point for each element in the cluster and take the average
			for j in range(0, len(clusterArray)):
				weightedX += clusterArray[j]['weightedPoint'][0]
				weightedY += clusterArray[j]['weightedPoint'][1]

			pair = [weightedX/len(clusterArray), weightedY/len(clusterArray)]
			grid['clusters'][i]['weightedPoint'] = pair

		#Remove elements
		grid.pop('elements', None)		

		print("Dumping grid to file")
		#Write the clusters to a file
   		#Dump into one json file using the name specified
		with open(fileName, 'w') as outfile:
			json.dump(grid, outfile, indent=4, sort_keys=True, separators=(',', ':'))		

		#Move to mapData
		#Create the corresponding mapData path
		temp = path.split("/")
        #Replace "rawData" at the front of the path with "mapData"
		mapDataPath = "mapData" + "/" + "/".join(temp[1:len(temp) - 1])

		#Create if it doesn't exist
		if not os.path.exists(mapDataPath):
			os.makedirs(mapDataPath)

   		#Move the newly created file to the correct directory
		try:
			os.rename(fileName, mapDataPath + "/" + fileName)
		except OSError:
     		#If the file exists, delete it and move the new file there
			print("File Exists: Overwriting existing file..")
			os.remove(mapDataPath + "/" + fileName)
			#copyfile(fileName, path + "/" + fileName)
			os.rename(fileName, mapDataPath + "/" + fileName)		

#getNeighbors(0, 0, [])
#sys.exit(0)

#Exit if not the correct number of arguments
if(len(sys.argv) != 2):
    printAllUsage()
    print(sys.argv)
    print(len(sys.argv))
    temp = ""
    for i in range(0, len(sys.argv)):
    	temp += sys.argv[i] + " "
    print("Invalid use:")
    print(temp)
    sys.exit(0)

if(sys.argv[1] == "-u" or sys.argv[1] == "-usage"):
    printAllUsage()
    sys.exit(0)

#Call the remove outliers function and pass it the path to the JSON file
createClusters(sys.argv[1])