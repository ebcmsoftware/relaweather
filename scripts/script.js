//:^)

var weather_data = {}; //want this to be global so we can use it l9r
var mode = 'current';
var d = new Date();
var hour = d.getHours();

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

function next() {
    switch(mode) {
        case 'current':
            mode = 'next';
            $('#weather_desc1').hide();
            $('#weather_desc2').show();
            $('#weather_desc3').hide();
            $('#prev').show();
            break;
        case 'next':
            mode = 'next_next';
            $('#weather_desc1').hide();
            $('#weather_desc2').hide();
            $('#weather_desc3').show();
            $('#next').hide();
            break;
    }
}

function prev() {
    switch(mode) {
        case 'next':
            mode = 'current';
            $('#weather_desc1').show();
            $('#weather_desc2').hide();
            $('#weather_desc3').hide();
            $('#prev').hide();
            break;
        case 'next_next':
            mode = 'next';
            $('#weather_desc1').hide();
            $('#weather_desc2').show();
            $('#weather_desc3').hide();
            $('#next').show();
            break;
    }
}

$(document).ready(function() {
    $('#prev').click(prev);
    $('#next').click(next);
    $('#prev').hide();
    $('#next').hide();
    $('#weather_desc2').hide();
    $('#weather_desc3').hide();
    $('#location_name').hide();
    $('#location_form').hide();
    $('#change_location').hide();
    if (navigator.geolocation) {
        use_geolocation();
    }
});

function draw_data(weather_data) {
    weather = [weather_data['current'], weather_data['next'], weather_data['next_next']]
    place = weather_data.city + ", " + weather_data.state

    show_weather(weather, place);
}

function get_success(data) {
    console.log("hey I got this data: " + data);
    weather_data = JSON.parse(data);
    draw_data(weather_data);
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

function show_weather(weather_strings, place_string){
    $('#location_name').html(place_string);
    $('#location_name').show();
    $('#weather_desc1').html(weather_strings[0]);
    $('#weather_desc2').html(weather_strings[1]);
    $('#weather_desc3').html(weather_strings[2]);
    $('#forecast').show();
    $('#location_form').hide();
    $('#change_location').show();
    $('#next').show();
    $('#browser_title').html(place_string + " Forecast");
}

