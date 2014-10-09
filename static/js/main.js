function initialize() {
    var mapOptions = {
        // center: { lat: -34.397, lng: 150.644},
        center: { lat: map_sy, lng: map_sx},
        zoom: 8
    };
    var map = new google.maps.Map(document.getElementById('map-canvas'), mapOptions);

    var drawingManager = new google.maps.drawing.DrawingManager();
    drawingManager.setMap(map);
}


google.maps.event.addDomListener(window, 'load', initialize);