//:^)

weather_data = {}; //want this to be global so we can use it l9r
mode = 'Today';
var d = new Date();
var hour = d.getHours();
if (hour >= 17) {
    switch_mode('Tomorrow'); //when to go to tonight/tomorrow night?
}

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

$(document).ready(function() {
    $('#switch_mode').hide();
    $('#location_name').hide();
    $('#location_form').hide();
    $('#change_location').hide();
    if (navigator.geolocation) {
        use_geolocation();
    }
});

function draw_data(weather_data) {
    var weather = mode + " <-- DEBUG";
    weather = weather_data[mode.toLowerCase()] || '';
    place = weather_data.city + ", " + weather_data.state
    show_weather(weather, place);
}

function get_success(data) {
    console.log("hey I got this data: " + data);
    weather_data = JSON.parse(data);
    draw_data(weather_data);
}

function switch_mode(new_mode) {
    if (new_mode.target) { //TODO: restructure this. i was writing this hastily
        if (mode == 'Today')
            new_mode = 'Tomorrow'
        if (mode == 'Tomorrow')
            new_mode = 'Today'
    }
    $('#switch_mode').html(mode + "'s forecast");
    mode = new_mode;
    draw_data(weather_data);
}

$('#switch_mode').click(switch_mode);

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
    $('#switch_mode').show();
}

