//:^)
$( document ).ready(function() {
    $('#location_name').hide();
});

if (navigator.geolocation) {
    var options = {
        enableHighAccuracy: true,
        maximumAge: 0
    };
    function success(position) {
        myLat = position.coords.latitude;
        myLng = position.coords.longitude;
        localStorage.setItem("user_lat", myLat);
        localStorage.setItem("user_lng", myLng);
        //alert('lat: ' + myLat + ' lng: ' + myLng);
        function post_success(data) {
            console.log("hey I got data");
            var weather_dat = JSON.parse(data);
            weather = "today it is " + weather_dat.today + " than yesterday";
            place = weather_dat.city + ", " + weather_dat.state
            show_weather(weather, place);
        }
        $.get('/api?lat='+myLat+'&lng='+myLng, post_success)
    }
    function error(err) {
        console.log('ERROR(' + err.code + '): ' + err.message);
    }
    navigator.geolocation.getCurrentPosition(success, error, options);
}

$('#zip_submit').click(function() {
    var zip_code = $('#zip_box').val(); 
    alert("lol haven't implemented this but we know ur zip is " + zip_code);
    show_weather("lol we don't know the weather today");

});

function show_weather(weather_string, place_string){
    $('#app_title').css('padding-top', '10px');
    $('#app_title').css('font_size', '2em');
    $('#location_name').show();
    $('#location_name').html(place_string);
    $('#weather_desc').html(weather_string);
    $('#weather_desc').show();
}
