//:^)
if (navigator.geolocation) {
    var options = {
        enableHighAccuracy: true,
        maximumAge: 0
    };
    function success(position) {
        myLat = position.coords.latitude;
        myLng = position.coords.longitude;
        alert('lat: ' + myLat + ' lng: ' + myLng);
    }
    function error(err) {
        alert('ERROR(' + err.code + '): ' + err.message);
    }
    navigator.geolocation.getCurrentPosition(success, error, options);
}
