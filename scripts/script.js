//:^)
function use_geolocation() {
    var options = {
        enableHighAccuracy: true,
        maximumAge: 0
    };
    function success(position) {
        myLat = position.coords.latitude;
        myLng = position.coords.longitude;
        localStorage.setItem("user_lat", myLat);
        localStorage.setItem("user_lng", myLng);
        $.get('/api?lat='+myLat+'&lng='+myLng, get_success);
    }
    function error(err) {
        console.log("you didn't want to give us your location");
        $('#location_form').show();
        $('#forecast').hide();
    }
    navigator.geolocation.getCurrentPosition(success, error, options);
}

$( document ).ready(function() {
    $('#location_name').hide();
    $('#location_form').hide();
    $('#change_location').hide();
    if (navigator.geolocation) {
        use_geolocation();
    }
});

function get_success(data) {
    console.log("hey I got this data: " + data);
    var weather_dat = JSON.parse(data);
    weather = weather_dat.today;
    place = weather_dat.city + ", " + weather_dat.state
    show_weather(weather, place);
}

$('#zip_submit').click(function() {
    var zip_code = $('#zip_box').val(); 
    if (zip_code.match(/^[0-9]{5}/) != null) {
        $.get('/api?zip='+zip_code, get_success);
    } else {
        alert("That's not a valid location.");
    }
});

$('#change_location').click(function() {
    $('#location_form').show();
    $('#forecast').hide();
    $('#change_location').hide();
});

$('#use_geolocation').click(function() {
    if (navigator.geolocation) {
        use_geolocation();
    }
});

function show_weather(weather_string, place_string){
    $('#location_name').html(place_string);
    $('#location_name').show();
    $('#weather_desc').html(weather_string);
    $('#forecast').show();
    $('#location_form').hide();
    $('#change_location').show();
}
