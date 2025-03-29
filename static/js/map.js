// map.js - Handles the interactive map functionality

document.addEventListener('DOMContentLoaded', function() {
    // Initialize the map if the element exists
    initMap();
});

// City coordinates for major Indian cities
const CITY_COORDINATES = {
    "Mumbai": [19.0760, 72.8777],
    "Delhi": [28.6139, 77.2090],
    "Bangalore": [12.9716, 77.5946],
    "Hyderabad": [17.3850, 78.4867],
    "Chennai": [13.0827, 80.2707],
    "Kolkata": [22.5726, 88.3639],
    "Pune": [18.5204, 73.8567],
    "Ahmedabad": [23.0225, 72.5714],
    "Jaipur": [26.9124, 75.7873],
    "Surat": [21.1702, 72.8311],
    "Lucknow": [26.8467, 80.9462],
    "Kanpur": [26.4499, 80.3319],
    "Nagpur": [21.1458, 79.0882],
    "Indore": [22.7196, 75.8577],
    "Thane": [19.2183, 72.9781],
    "Bhopal": [23.2599, 77.4126],
    "Visakhapatnam": [17.6868, 83.2185],
    "Patna": [25.5941, 85.1376],
    "Vadodara": [22.3072, 73.1812],
    "Ghaziabad": [28.6692, 77.4538]
};

// Map instance
let map;
let cityMarkers = {};
let weatherData = {};
let disasterPredictions = {};

function initMap() {
    const mapContainer = document.getElementById('india-map');
    if (!mapContainer) return;
    
    // Initialize the map centered on India
    map = L.map('india-map').setView([22.5726, 78.9629], 5);
    
    // Add OpenStreetMap tile layer
    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors',
        maxZoom: 18
    }).addTo(map);
    
    // Add markers for major cities
    addCityMarkers();
    
    // Fetch weather data for all cities
    fetchAllCitiesWeatherData();
    
    // Fetch disaster predictions for all cities
    fetchAllCitiesPredictions();
}

function addCityMarkers() {
    for (const city in CITY_COORDINATES) {
        const [lat, lng] = CITY_COORDINATES[city];
        
        // Create a marker
        const marker = L.marker([lat, lng]).addTo(map);
        
        // Add a basic popup
        marker.bindPopup(`<b>${city}</b><br>Loading data...`);
        
        // Store the marker reference
        cityMarkers[city] = marker;
        
        // Add click event
        marker.on('click', function() {
            updateMarkerPopup(city);
        });
    }
}

function updateMarkerPopup(city) {
    const marker = cityMarkers[city];
    if (!marker) return;
    
    // Get weather data and predictions for this city
    const cityWeather = weatherData[city];
    const cityPredictions = disasterPredictions[city];
    
    let popupContent = `<div class="map-popup"><h5>${city}</h5>`;
    
    // Add weather data if available
    if (cityWeather) {
        popupContent += `
            <div class="weather-info">
                <p><strong>Temperature:</strong> ${cityWeather.temperature}°C</p>
                <p><strong>Conditions:</strong> ${cityWeather.weather_description}</p>
            </div>
        `;
    }
    
    // Add disaster predictions if available
    if (cityPredictions && cityPredictions.length > 0) {
        popupContent += `<div class="disaster-predictions mt-2"><strong>Risk Alerts:</strong><ul>`;
        
        cityPredictions.forEach(prediction => {
            const severityClass = getSeverityColorClass(prediction.severity);
            popupContent += `<li class="${severityClass}">${prediction.disaster_type} - Severity: ${prediction.severity}/5</li>`;
        });
        
        popupContent += `</ul></div>`;
    } else {
        popupContent += `<p>No current disaster risks detected.</p>`;
    }
    
    // Add link to dashboard with this city pre-selected
    popupContent += `<a href="/dashboard?city=${encodeURIComponent(city)}" class="btn btn-sm btn-primary mt-2">View Details</a>`;
    
    popupContent += `</div>`;
    
    // Update the popup content
    marker.setPopupContent(popupContent);
    marker.openPopup();
}

function fetchAllCitiesWeatherData() {
    // Show loading indicator
    const mapLoading = document.getElementById('map-loading');
    if (mapLoading) {
        mapLoading.classList.remove('d-none');
    }
    
    // Create promises for all city weather requests
    const weatherPromises = Object.keys(CITY_COORDINATES).map(city => {
        return fetch(`/api/weather/${city}`)
            .then(response => {
                if (!response.ok) {
                    throw new Error(`Weather data fetch failed for ${city}`);
                }
                return response.json();
            })
            .then(data => {
                // Store the weather data
                weatherData[city] = data;
                
                // Update marker based on weather
                updateMarkerStyle(city, data);
                
                return data;
            })
            .catch(error => {
                console.error(`Error fetching weather data for ${city}:`, error);
                return null;
            });
    });
    
    // When all weather data is fetched
    Promise.all(weatherPromises)
        .then(() => {
            // Hide loading indicator
            if (mapLoading) {
                mapLoading.classList.add('d-none');
            }
        })
        .catch(error => {
            console.error('Error fetching all weather data:', error);
            // Hide loading indicator
            if (mapLoading) {
                mapLoading.classList.add('d-none');
            }
        });
}

function updateMarkerStyle(city, weatherData) {
    const marker = cityMarkers[city];
    if (!marker || !weatherData) return;
    
    // Default marker icon
    let iconUrl = 'https://cdn.jsdelivr.net/npm/leaflet@1.7.1/dist/images/marker-icon.png';
    
    // Set icon based on weather
    const weatherCode = weatherData.weathercode;
    
    if (weatherCode === 0) {
        // Clear sky - sun icon
        marker.setIcon(createMarkerIcon('#FFD700'));
    } else if (weatherCode >= 1 && weatherCode <= 3) {
        // Partly cloudy to overcast
        marker.setIcon(createMarkerIcon('#A9A9A9'));
    } else if (weatherCode >= 51 && weatherCode <= 67) {
        // Rain - blue icon
        marker.setIcon(createMarkerIcon('#1E90FF'));
    } else if (weatherCode >= 71 && weatherCode <= 77) {
        // Snow - white icon
        marker.setIcon(createMarkerIcon('#FFFFFF'));
    } else if (weatherCode >= 95 && weatherCode <= 99) {
        // Thunderstorm - purple icon
        marker.setIcon(createMarkerIcon('#9370DB'));
    }
}

function createMarkerIcon(color) {
    return L.divIcon({
        className: 'custom-div-icon',
        html: `<div style="background-color: ${color}; width: 12px; height: 12px; border-radius: 50%; border: 2px solid #FFF;"></div>`,
        iconSize: [12, 12],
        iconAnchor: [6, 6]
    });
}

function fetchAllCitiesPredictions() {
    // Create promises for all city prediction requests
    const predictionPromises = Object.keys(CITY_COORDINATES).map(city => {
        return fetch(`/api/disasters/predictions/${city}`)
            .then(response => {
                if (!response.ok) {
                    throw new Error(`Predictions fetch failed for ${city}`);
                }
                return response.json();
            })
            .then(data => {
                // Store the predictions
                disasterPredictions[city] = data;
                
                // If there are high-severity predictions, update the marker
                if (data && data.length > 0) {
                    const highestSeverity = Math.max(...data.map(pred => pred.severity));
                    if (highestSeverity >= 4) {
                        // High severity - highlight the marker
                        highlightCityWithRisk(city, highestSeverity);
                    }
                }
                
                return data;
            })
            .catch(error => {
                console.error(`Error fetching predictions for ${city}:`, error);
                return null;
            });
    });
    
    // When all prediction data is fetched
    Promise.all(predictionPromises)
        .then(() => {
            console.log('All prediction data fetched');
        })
        .catch(error => {
            console.error('Error fetching all prediction data:', error);
        });
}

function highlightCityWithRisk(city, severity) {
    const marker = cityMarkers[city];
    if (!marker) return;
    
    let riskColor;
    
    // Set color based on severity
    if (severity === 5) {
        riskColor = '#FF0000'; // Red for highest severity
    } else if (severity === 4) {
        riskColor = '#FF4500'; // OrangeRed for high severity
    } else if (severity === 3) {
        riskColor = '#FFA500'; // Orange for medium severity
    } else {
        riskColor = '#FFFF00'; // Yellow for lower severity
    }
    
    // Create a pulsing circle around the marker
    L.circle([CITY_COORDINATES[city][0], CITY_COORDINATES[city][1]], {
        color: riskColor,
        fillColor: riskColor,
        fillOpacity: 0.3,
        radius: 30000, // 30km radius
        className: 'pulsing-circle'
    }).addTo(map);
    
    // Create a custom icon with an alert symbol
    marker.setIcon(L.divIcon({
        className: 'custom-div-icon',
        html: `<div style="background-color: ${riskColor}; width: 14px; height: 14px; border-radius: 50%; border: 2px solid #FFF; box-shadow: 0 0 10px ${riskColor}"></div>`,
        iconSize: [14, 14],
        iconAnchor: [7, 7]
    }));
}

function getSeverityColorClass(severity) {
    switch (severity) {
        case 5:
            return 'text-danger';
        case 4:
            return 'text-warning';
        case 3:
            return 'text-warning';
        case 2:
            return 'text-info';
        case 1:
            return 'text-info';
        default:
            return '';
    }
}
