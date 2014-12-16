//:^)
$( document ).ready(function() {
    $('#location_name').hide();
});

function get_success(data) {
    console.log("hey I got data");
    var weather_dat = JSON.parse(data);
    weather = "today it is " + weather_dat.today + " than yesterday";
    place = weather_dat.city + ", " + weather_dat.state
    show_weather(weather, place);
}

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
        $.get('/api?lat='+myLat+'&lng='+myLng, get_success);
    }
    function error(err) {
        console.log('ERROR(' + err.code + '): ' + err.message);
    }
    navigator.geolocation.getCurrentPosition(success, error, options);
}

$('#zip_submit').click(function() {
        var zip_code = $('#zip_box').val(); 
        if (zip_code.match(/^[0-9]{5}/) != null) {
            $.get('/api?zip='+zip_code, get_success);
        } else {
                alert("That's not a valid location.");
        }
});

function show_weather(weather_string, place_string){
    $('#app_title').css('padding-top', '10px');
    $('#app_title').css('font_size', '2em');
    $('#location_name').html(place_string);
    $('#location_name').show();
    $('#weather_desc').html(weather_string);
    $('#weather_desc').show();
    $('#location_form').hide();
}
