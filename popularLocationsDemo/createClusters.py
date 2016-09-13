import sys
import json
import math
#Given the path a JSON file, creates another JSON file of clusters

def printAllUsage():
    print("Usage: python createClusters.py [pathToJSON]")

#Given the JSON file data
#Return the topleft-most bound lat lng
#Takes into account quadrants
def getTopLeftGridBound(data):


	left = float(data['photos']['photo'][0]['longitude'])
	top = float(data['photos']['photo'][0]['latitude'])
	print("init: " + str(left) + " " + str(top))

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

	return grid

def createClusters(path):
	print("Going to create clusters of the file at " + path)

	with open(path) as data_file:
		#Open JSOn file
		data = json.load(data_file)

        #Step1: Create Grid
		gridBounds = getGridBounds(data)
		grid = createGrid(gridBounds[0], gridBounds[1], 10)

		print("Dumping grid to file")
		#Write the clusters to a file
   		#Dump into one json file using the name specified
		with open("clusterTest" + ".json", 'w') as outfile:
			json.dump(grid, outfile, indent=4, sort_keys=True, separators=(',', ':'))		

#Exit if not the correct number of arguments
if(len(sys.argv) != 2):
    printAllUsage()
    sys.exit(0)

if(sys.argv[1] == "-u" or sys.argv[1] == "-usage"):
    printAllUsage()
    sys.exit(0)

#Call the remove outliers function and pass it the path to the JSON file
createClusters(sys.argv[1])