// Creates and returns a new google map instance, centered in Manhattan
function initMap() {
  var latLong = {lat: 40.780341, lng: -73.954019};

  map = new google.maps.Map(document.getElementById('map'), {
  zoom: 10,
  center: latLong
  });

  return map;
}

// Given a list of addresses, finds latlong and places a pin on the map
function addMarkers (addresses, map) {
  var i, address;
  var geocoder = new google.maps.Geocoder();
  for (i=0;i<addresses.length;i++){
    address = addresses[i];
    // Geocode and pin each address
    geocoder.geocode({'address': address}, function(results, status){
      var marker = new google.maps.Marker({
        map: map,
        position: results[0].geometry.location
      });
    })
  }
}
