//List of city objects that remains unchanged
//City objects are: {country, city, timeZone, time, key}
var cities = [];
//List of city objects to display. Starts off the same as cities but can become smaller depending
//on the filters the user applies
var citiesToDisplay = [];
//Web worker
var w;
//If a column is sorted, the respective variable is set to true. This allows the column to be reverse
//sorted when clicked again
var countrySorted = true, citySorted = false, timeZoneSorted = false;

function startWorker() {
	if(typeof(Worker) !== "undefined") {
		if(typeof(w) == "undefined") {
			w = new Worker("demo_worker.js");
		}
		w.onmessage = function(event) {
			document.getElementById("counter").innerHTML = event.data;
			updateTime();
		};
	} else {
		document.getElementById("counter").innerHTML = "Sorry, your browser does not support Web Workers...";
	}
}

//Helper function
//When given a countryCity in the format: Country/City, returns the country as a string
function getCountry(countryCity){
   //Search for the position of the slash
   var pos = countryCity.search("/");

   //If only the country is listed
   if(pos == -1) {
   	return countryCity;
   }

   return countryCity.slice(0, pos);
 }

//Helper function
//When given a countryCity in the format: Country/City, returns the city as a string
function getCity(countryCity){
   //Search for the position of the slash
   var pos = countryCity.search("/");

   return countryCity.slice(pos+1);
 }

//When this function is called, the cities variable is populated with all of the cities retrieved from moment.js
function init() {
   //Get a starting date and then convert each city to that date
   var date = moment().tz("America/Los_Angeles").format('h:mm:ss A| M/D/YYYY');

   //Retrieve every city
   var zones = moment.tz.names();
   //Loop index
   var i = 0;
   //Where a new city is constructed before being pushed into the cities array
   var tempCity;
   //Temp variables
   var tempTimeZone;
   var tempTime;


   //Create every city object and add it to the cities variable
   for(i = 0; i < zones.length; i++) {
   	  //var date = moment().tz(zones[i]).format('h:mm:ss A| M/D/YYYY z');
      //Get the timezone of the given zone
      tempTimeZone = moment().tz(zones[i]).format('z');
      //Get the time of the given zone
      tempTime = moment().tz(zones[i]).format('h:mm:ss A | M/D/YYYY');

      //Create city object
      tempCity = {country: getCountry(zones[i]), city: getCity(zones[i]), timeZone: tempTimeZone, time: tempTime, key: zones[i]};

      cities.push(tempCity);

    }
  }

//Initial display function that is called
//Creates table with all city objects from cities array
function initDisplayCities() {
	var i = 0;
	var table, row, cell1, cell2, cell3, cell4;

	table = document.getElementById("timeTable");

	for(i = 0; i < cities.length; i++) {

      //Insert city in the next row
      row = table.insertRow(i+1);
      //Create four columns
      cell1 = row.insertCell(0);
      cell2 = row.insertCell(1);
      cell3 = row.insertCell(2);
      cell4 = row.insertCell(3);
      //Write each field to the correct column
      cell1.innerHTML = cities[i].country;
      cell2.innerHTML = cities[i].city;
      cell3.innerHTML = cities[i].timeZone;
      cell4.innerHTML = cities[i].time;
    }

   //Update cities that are being displayed
   citiesToDisplay = cities.slice();
 }

//Called when the cities to display have been changed/been sorted
//Updates the table's values from the citiesToDisplay array
function updateTable() {
	var i;
	var row, cell1, cell2, cell3, cell4;
	var table = document.getElementById("timeTable");

   //Update each row with the updated citiesToDisplay info
   for(i = 0; i < citiesToDisplay.length; i++) {
   	  //Access row
   	  row = table.rows[i+1];
      //Update the row's cells
      row.cells[0].innerHTML = citiesToDisplay[i].country;
      row.cells[1].innerHTML = citiesToDisplay[i].city;
      row.cells[2].innerHTML = citiesToDisplay[i].timeZone;
      row.cells[3].innerHTML = citiesToDisplay[i].time;
    }
  }

//Called by the web worker
//Updates the .time field in each object in the citiesToDisplay array
function updateTime() {

   //Update each citiesToDisplay's time
   for(i = 0; i < citiesToDisplay.length; i++) {
      //Get the time of the given zone, using the citiesToDisplay key
      citiesToDisplay[i].time = moment().tz(citiesToDisplay[i].key).format('h:mm:ss A| M/D/YYYY');   
    }

   //Reflects the changes in time on the table
   updateTable();
 }
 
 //Called when cities are added or removed from citiesToDisplay
 //Removes/adds the cities from the time table
 //This was made a separate function from updateTable to avoid the time table from being needlessly
 //updated every webworker tick; cities should only be added/removed when the fitler field is changed
 function changeTable() {
   var i;
   var table = document.getElementById("timeTable");
   var row, cell1, cell2, cell3, cell4;

     //Delete all table rows
     while(table.rows.length > 1) {
      table.deleteRow(1);
    }

     //Insert newly updated rows from citiesToDisplay
     for(i = 0; i < citiesToDisplay.length; i++) {

      //Insert city in the next row
      row = table.insertRow(i+1);
      //Create four columns
      cell1 = row.insertCell(0);
      cell2 = row.insertCell(1);
      cell3 = row.insertCell(2);
      cell4 = row.insertCell(3);
      //Write each field to the correct column
      cell1.innerHTML = cities[i].country;
      cell2.innerHTML = cities[i].city;
      cell3.innerHTML = cities[i].timeZone;
      cell4.innerHTML = cities[i].time;
    }

  }

//Helper function that compares the properties of two city objects
function compareCities(a, b) {
	if(a.city < b.city) {
		return -1;
	}
	else if(a.city > b.city) {
		return 1;
	}
	return 0;
}

//Helper function to compare the properties of two city objects
function compareCountries(a, b) {
	if(a.country < b.country) {
		return -1;
	}
	else if(a.country > b.country) {
		return 1;
	}
	return 0;	
}

//Helper function to compare the properties of two city objects
function compareTimeZone(a, b) {
	if(a.timeZone < b.timeZone) {
		return -1;
	}
	else if(a.timeZone > b.timeZone) {
		return 1;
	}
	return 0;	
}

function sortByCountry() {
   //If already sorted by country, then reverse sort
   if(countrySorted == true) {
   	citiesToDisplay.reverse(compareCountries);
   	countrySorted = false;
   }
   else {
      //Else not sorted by country, so sort
      citiesToDisplay.sort(compareCountries);
      countrySorted = true;
    }

    citySorted = false;
    timeZoneSorted = false;

    updateTable();
  }

  function sortByCity() {
   //If already sorted by city, then reverse sort
   if(citySorted == true) {
   	citiesToDisplay.reverse(compareCities);
   	citySorted = false;
   }
   else {
      //Else not sorted, so sort
      citiesToDisplay.sort(compareCities);
      citySorted = true;
    }

    countrySorted = false;
    timeZoneSorted = false;

    updateTable();
  }


  function sortByTimeZone() {
   //If already sorted by city, then reverse sort
   if(timeZoneSorted == true) {
   	citiesToDisplay.reverse(compareTimeZone);
   	timeZoneSorted = false;
   }
   else {
      //Else not sorted, so sort
      citiesToDisplay.sort(compareTimeZone);
      timeZoneSorted = true;
    }

    countrySorted = false;
    citySorted = false;

    updateTable();
  }

   //Called when the country filter field is changed
   //Changes the cities to display, to only cities that has a country with a substring
   //matching the text argument
   function filterCountry(text) {
     console.log(text);

     //Used to index through the countries
     var i;

     //Empty cities to display
     citiesToDisplay = [];

     for(i = 0; i < cities.length; i++) {
        //If the country contains the text
        if(cities[i].country.includes(text)) {
           //Add it to the cities to be displayed
           citiesToDisplay.push(cities[i]);
         }
       }
       changeTable();

     }

//Initialize all city objects
window.onload = function() {
  init();
  initDisplayCities();
  startWorker();
}

//When the coutnry filter field is changed, call the filterCountry function and give it
//the text field's value
$(document).ready(function(){
  $("#countryFilter").keyup(function() {
    filterCountry($(this).val());
  });
});

