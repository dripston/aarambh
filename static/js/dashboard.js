// dashboard.js - Handles the dashboard functionality

document.addEventListener('DOMContentLoaded', function() {
    // Initialize the city selector
    initCitySelector();
    
    // Initialize weather data display
    updateWeatherData();
    
    // Initialize forecast chart
    initForecastChart();
    
    // Set up refresh interval (every 15 minutes)
    setInterval(updateWeatherData, 15 * 60 * 1000);
});

function initCitySelector() {
    const citySelector = document.getElementById('citySelector');
    if (!citySelector) return;
    
    citySelector.addEventListener('change', function() {
        // Get the selected city
        const selectedCity = this.value;
        
        // Update the URL with the selected city
        const currentUrl = new URL(window.location.href);
        currentUrl.searchParams.set('city', selectedCity);
        window.history.pushState({}, '', currentUrl);
        
        // Update the weather data and forecast
        updateWeatherData();
        updateDisasterPredictions();
    });
}

function updateWeatherData() {
    // Get the selected city
    const citySelector = document.getElementById('citySelector');
    if (!citySelector) return;
    
    const selectedCity = citySelector.value;
    
    // Show loading indicators
    document.getElementById('weather-loading').classList.remove('d-none');
    
    // Fetch current weather data
    fetch(`/api/weather/${selectedCity}`)
        .then(response => {
            if (!response.ok) {
                throw new Error('Weather data fetch failed');
            }
            return response.json();
        })
        .then(data => {
            // Update weather information in the UI
            updateWeatherUI(data);
            // Hide loading indicator
            document.getElementById('weather-loading').classList.add('d-none');
        })
        .catch(error => {
            console.error('Error fetching weather data:', error);
            document.getElementById('weather-loading').classList.add('d-none');
            // Show error message
            document.getElementById('weather-error').classList.remove('d-none');
            document.getElementById('weather-error').textContent = 'Failed to load weather data. Please try again later.';
        });
    
    // Fetch forecast data and update chart
    fetch(`/api/forecast/${selectedCity}`)
        .then(response => {
            if (!response.ok) {
                throw new Error('Forecast data fetch failed');
            }
            return response.json();
        })
        .then(data => {
            // Update forecast chart
            updateForecastChart(data);
        })
        .catch(error => {
            console.error('Error fetching forecast data:', error);
        });
    
    // Update disaster predictions
    updateDisasterPredictions();
}

function updateWeatherUI(weatherData) {
    if (!weatherData) return;
    
    // Update current weather display
    document.getElementById('current-location').textContent = weatherData.city;
    document.getElementById('current-temperature').textContent = `${weatherData.temperature}°C`;
    document.getElementById('current-description').textContent = weatherData.weather_description;
    
    // Update detailed weather information
    document.getElementById('current-humidity').textContent = `${weatherData.humidity}%`;
    document.getElementById('current-wind').textContent = `${weatherData.windspeed} km/h`;
    document.getElementById('current-precipitation').textContent = `${weatherData.precipitation} mm`;
    
    // Update weather icon based on weather code
    updateWeatherIcon(weatherData.weathercode);
    
    // Update weather card background based on conditions
    updateWeatherCardBackground(weatherData);
    
    // Update last updated time
    const lastUpdated = new Date().toLocaleTimeString();
    document.getElementById('last-updated').textContent = `Last updated: ${lastUpdated}`;
}

function updateWeatherIcon(weatherCode) {
    let iconClass = 'fas fa-cloud'; // Default icon
    
    // Map weather codes to Font Awesome icons
    if (weatherCode === 0) {
        iconClass = 'fas fa-sun'; // Clear sky
    } else if (weatherCode === 1 || weatherCode === 2) {
        iconClass = 'fas fa-cloud-sun'; // Partly cloudy
    } else if (weatherCode === 3) {
        iconClass = 'fas fa-cloud'; // Overcast
    } else if (weatherCode >= 45 && weatherCode <= 48) {
        iconClass = 'fas fa-smog'; // Fog
    } else if ((weatherCode >= 51 && weatherCode <= 55) || (weatherCode >= 61 && weatherCode <= 65)) {
        iconClass = 'fas fa-cloud-rain'; // Rain
    } else if (weatherCode >= 71 && weatherCode <= 77) {
        iconClass = 'fas fa-snowflake'; // Snow
    } else if (weatherCode >= 80 && weatherCode <= 82) {
        iconClass = 'fas fa-cloud-showers-heavy'; // Rain showers
    } else if (weatherCode >= 95 && weatherCode <= 99) {
        iconClass = 'fas fa-bolt'; // Thunderstorm
    }
    
    // Update the icon
    const weatherIcon = document.getElementById('weather-icon');
    if (weatherIcon) {
        weatherIcon.className = iconClass;
    }
}

function updateWeatherCardBackground(weatherData) {
    const weatherCard = document.getElementById('weather-card');
    if (!weatherCard) return;
    
    // Remove any existing conditional classes
    weatherCard.classList.remove('bg-warning', 'bg-danger', 'bg-info');
    
    // Set background based on conditions
    if (weatherData.temperature > 35) {
        // Hot temperature
        weatherCard.classList.add('bg-danger');
    } else if (weatherData.weathercode >= 95) {
        // Thunderstorm
        weatherCard.classList.add('bg-warning');
    } else if ((weatherData.weathercode >= 51 && weatherData.weathercode <= 65) || 
               (weatherData.weathercode >= 80 && weatherData.weathercode <= 82)) {
        // Rain
        weatherCard.classList.add('bg-info');
    }
}

function initForecastChart() {
    // Get the canvas element
    const ctx = document.getElementById('forecastChart');
    if (!ctx) return;
    
    // Initialize an empty chart
    window.forecastChart = new Chart(ctx, {
        type: 'line',
        data: {
            labels: [],
            datasets: [
                {
                    label: 'Max Temperature (°C)',
                    data: [],
                    borderColor: 'rgba(255, 99, 132, 1)',
                    backgroundColor: 'rgba(255, 99, 132, 0.2)',
                    tension: 0.1
                },
                {
                    label: 'Min Temperature (°C)',
                    data: [],
                    borderColor: 'rgba(54, 162, 235, 1)',
                    backgroundColor: 'rgba(54, 162, 235, 0.2)',
                    tension: 0.1
                },
                {
                    label: 'Precipitation (mm)',
                    data: [],
                    borderColor: 'rgba(75, 192, 192, 1)',
                    backgroundColor: 'rgba(75, 192, 192, 0.2)',
                    tension: 0.1,
                    yAxisID: 'y1'
                }
            ]
        },
        options: {
            responsive: true,
            plugins: {
                title: {
                    display: true,
                    text: '5-Day Weather Forecast'
                },
                tooltip: {
                    mode: 'index',
                    intersect: false
                }
            },
            scales: {
                y: {
                    title: {
                        display: true,
                        text: 'Temperature (°C)'
                    }
                },
                y1: {
                    position: 'right',
                    title: {
                        display: true,
                        text: 'Precipitation (mm)'
                    },
                    grid: {
                        drawOnChartArea: false
                    }
                }
            }
        }
    });
}

function updateForecastChart(forecastData) {
    if (!window.forecastChart || !forecastData || !forecastData.length) return;
    
    // Extract data for the chart
    const labels = forecastData.map(day => {
        const date = new Date(day.date);
        return date.toLocaleDateString('en-US', { weekday: 'short', month: 'short', day: 'numeric' });
    });
    
    const maxTemps = forecastData.map(day => day.temperature_max);
    const minTemps = forecastData.map(day => day.temperature_min);
    const precipitation = forecastData.map(day => day.precipitation);
    
    // Update chart data
    window.forecastChart.data.labels = labels;
    window.forecastChart.data.datasets[0].data = maxTemps;
    window.forecastChart.data.datasets[1].data = minTemps;
    window.forecastChart.data.datasets[2].data = precipitation;
    
    // Update chart
    window.forecastChart.update();
}

function updateDisasterPredictions() {
    // Get the selected city
    const citySelector = document.getElementById('citySelector');
    if (!citySelector) return;
    
    const selectedCity = citySelector.value;
    const disasterContainer = document.getElementById('disaster-predictions');
    
    if (!disasterContainer) return;
    
    // Show loading indicator
    document.getElementById('predictions-loading').classList.remove('d-none');
    
    // Fetch disaster predictions
    fetch(`/api/disasters/predictions/${selectedCity}`)
        .then(response => {
            if (!response.ok) {
                throw new Error('Disaster predictions fetch failed');
            }
            return response.json();
        })
        .then(data => {
            // Hide loading indicator
            document.getElementById('predictions-loading').classList.add('d-none');
            
            // Clear previous disaster predictions
            disasterContainer.innerHTML = '';
            
            if (data.length === 0) {
                // Show no predictions message
                disasterContainer.innerHTML = `
                    <div class="alert alert-info">
                        No disaster predictions for ${selectedCity} at this time.
                    </div>
                `;
                return;
            }
            
            // Add disaster predictions
            data.forEach(prediction => {
                // Create a card for each prediction
                const cardColorClass = getDisasterSeverityClass(prediction.severity);
                
                const predictionCard = document.createElement('div');
                predictionCard.className = `card mb-3 ${cardColorClass}`;
                
                predictionCard.innerHTML = `
                    <div class="card-header d-flex justify-content-between align-items-center">
                        <h5 class="m-0">${prediction.disaster_type}</h5>
                        <span class="badge bg-${getSeverityBadgeColor(prediction.severity)}">
                            Severity: ${prediction.severity}/5
                        </span>
                    </div>
                    <div class="card-body">
                        <p class="card-text">${prediction.description}</p>
                        <p class="mb-0"><strong>Probability:</strong> ${Math.round(prediction.probability * 100)}%</p>
                        <p class="mb-0"><strong>Valid until:</strong> ${prediction.valid_until}</p>
                        <div class="mt-3">
                            <strong>Precautions:</strong>
                            <ul class="mb-0">
                                ${prediction.precautions.map(p => `<li>${p}</li>`).join('')}
                            </ul>
                        </div>
                    </div>
                `;
                
                disasterContainer.appendChild(predictionCard);
            });
        })
        .catch(error => {
            console.error('Error fetching disaster predictions:', error);
            // Hide loading indicator
            document.getElementById('predictions-loading').classList.add('d-none');
            // Show error message
            disasterContainer.innerHTML = `
                <div class="alert alert-danger">
                    Failed to load disaster predictions. Please try again later.
                </div>
            `;
        });
}

function getDisasterSeverityClass(severity) {
    switch (severity) {
        case 5:
            return 'border-danger';
        case 4:
            return 'border-warning';
        case 3:
            return 'border-warning';
        case 2:
            return 'border-info';
        case 1:
            return 'border-info';
        default:
            return '';
    }
}

function getSeverityBadgeColor(severity) {
    switch (severity) {
        case 5:
            return 'danger';
        case 4:
            return 'warning';
        case 3:
            return 'warning';
        case 2:
            return 'info';
        case 1:
            return 'info';
        default:
            return 'secondary';
    }
}
