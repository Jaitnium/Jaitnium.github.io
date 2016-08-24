from urllib.request import urlopen
from bs4 import BeautifulSoup
import json

class Dog:
	def __init__(self, name, infoPage, imgLink, intelligence, shedding, energy, size):
		self.name = name
		self.infoPage = infoPage
		self.imgLink = imgLink
		self.intelligence = intelligence
		self.shedding = shedding
		self.energy = energy
		self.size = size

	def printDog(self):
		print("Name: " + self.name + " Intelligence: " + self.intelligence + " Shedding: "
			+ self.shedding + " Energy: " + self.energy + " Size: " + self.size)

def getDogBreeds(links):

	breeds=[];

	for index in range(len(links)):
		#Add each name to an array to return
		breeds.append(links[index].string)
		#print(index)
		#print(links[index].string)
		#print("\n")

	return breeds

def getInfoPages(links):

	infoPages=[];

	for index in range(len(links)):
		infoPages.append(links[index].get('href'))

	return infoPages

#Helper Function
#Returns the value of the desired string content, based on
#the layout of dogtime.com
def findElementValue(soup, string):
   for tag in soup.findAll('span'):
   		if tag.string == string:
   			tag = tag.findNextSibling()
   			children = tag.findChildren()
   			for child in children:
   				return child.string

#Given the dog's name and info page link
#Returns a Dog class
def fetchDogInfo(name, link):
   intelligence = None; shedding = None; energy = None; size = None; imgLink = None
   print(name)
   print(link)
   page = urlopen(link);
   soup = BeautifulSoup(page, "html.parser")
   soup.prettify().encode('UTF-8')

   #Get link to img   
   for tag in soup.findAll("div", {"class" : "article-content"}):
      imgChild = tag.findChildren()[0]
      imgLink = (imgChild['src'])

   #soup.findAll("span", {"class" : "characteristic item-trigger-title"})

   #Find Intelligence
   intelligence = findElementValue(soup, "Intelligence")
   print(intelligence)

   #Find Shedding
   shedding = findElementValue(soup, "Amount Of Shedding")
   print(shedding)

   #Find Energy
   energy = findElementValue(soup, "Energy Level")
   print(energy)

   #Find Size
   size = findElementValue(soup, "Size")
   print(size)

   dog = Dog(name, link, imgLink, intelligence, shedding, energy, size)
   return dog

#Where the list of dog breeds are stored
dogBreeds = []
#List of links to each breed's info page
infoPages = []

url = "http://dogtime.com/dog-breeds"
page = urlopen(url)
soup = BeautifulSoup(page, "html.parser")

#Print out the page's contents
print(soup.prettify().encode('UTF-8'))
print('\n')

#Retreive each post-title class which contains both the dog breed names and
#links to each dog's info page
links = soup.findAll("a", {"class" : "post-title"})

#Get the list of dog breeds
breeds = getDogBreeds(links)
#Get the links to each dog's info page
infoPages = getInfoPages(links)

for index in range(len(breeds)):
	print(breeds[index])

for index in range(len(breeds)):
	print(infoPages[index])

tempDog = None

#for index in range(len(breeds)):
#	tempDog = fetchDogInfo(breeds[index], infoPages[index])
#	tempDog.printDog()

#tempDog = fetchDogInfo(breeds[0], infoPages[0])

data=[]

#file = open("breeds.js", "w")
file = open("breeds.json", "w")

#data.append("{dogBreeds:")

for index in range(len(breeds)):
	tempDog = fetchDogInfo(breeds[index], infoPages[index])

	data.append({
		"breedName": tempDog.name,
		"link": tempDog.infoPage,
		"imgLink": tempDog.imgLink,
		"intelligence": tempDog.intelligence,
		"shedding": tempDog.shedding,
		"energy": tempDog.energy,
		"size": tempDog.size
	})

output = {"dogBreeds": data}

#with open("breeds.json", "w") as outf:
	#json.dump(output, file, sort_keys=True, indent=4)
#	json.dump(output, file)


with open("breeds.json", "w") as outf:
	#json.dump(output, file, sort_keys=True, indent=4)
	json.dump(output, file)

