// charts.js - Handles various chart visualizations

document.addEventListener('DOMContentLoaded', function() {
    // Initialize historical disaster chart
    initHistoricalDisasterChart();
    
    // Initialize prediction distribution chart
    initPredictionDistributionChart();
});

function initHistoricalDisasterChart() {
    const ctx = document.getElementById('historicalDisasterChart');
    if (!ctx) return;
    
    // Show loading indicator
    document.getElementById('historical-chart-loading').classList.remove('d-none');
    
    // Fetch historical disaster data
    fetch('/api/disasters/historical')
        .then(response => {
            if (!response.ok) {
                throw new Error('Historical disaster data fetch failed');
            }
            return response.json();
        })
        .then(data => {
            // Hide loading indicator
            document.getElementById('historical-chart-loading').classList.add('d-none');
            
            // Process the data for the chart
            const disasterCounts = processHistoricalData(data);
            
            // Create the chart
            createHistoricalDisasterChart(ctx, disasterCounts);
        })
        .catch(error => {
            console.error('Error fetching historical disaster data:', error);
            // Hide loading indicator
            document.getElementById('historical-chart-loading').classList.add('d-none');
            // Show error message
            document.getElementById('historical-chart-error').classList.remove('d-none');
            document.getElementById('historical-chart-error').textContent = 'Failed to load historical disaster data. Please try again later.';
        });
}

function processHistoricalData(disasters) {
    // Count disasters by type
    const disasterCounts = {};
    
    disasters.forEach(disaster => {
        const type = disaster.type || 'Unknown';
        if (disasterCounts[type]) {
            disasterCounts[type]++;
        } else {
            disasterCounts[type] = 1;
        }
    });
    
    return disasterCounts;
}

function createHistoricalDisasterChart(ctx, disasterCounts) {
    // Get disaster types and counts
    const types = Object.keys(disasterCounts);
    const counts = Object.values(disasterCounts);
    
    // Define colors for different disaster types
    const colors = [
        'rgba(255, 99, 132, 0.8)',
        'rgba(54, 162, 235, 0.8)',
        'rgba(255, 206, 86, 0.8)',
        'rgba(75, 192, 192, 0.8)',
        'rgba(153, 102, 255, 0.8)',
        'rgba(255, 159, 64, 0.8)',
        'rgba(199, 199, 199, 0.8)',
        'rgba(83, 102, 255, 0.8)',
        'rgba(40, 159, 64, 0.8)',
        'rgba(210, 99, 132, 0.8)'
    ];
    
    // Create chart
    new Chart(ctx, {
        type: 'bar',
        data: {
            labels: types,
            datasets: [{
                label: 'Number of Disasters',
                data: counts,
                backgroundColor: colors.slice(0, types.length),
                borderColor: colors.slice(0, types.length).map(color => color.replace('0.8', '1')),
                borderWidth: 1
            }]
        },
        options: {
            responsive: true,
            plugins: {
                legend: {
                    display: false
                },
                title: {
                    display: true,
                    text: 'Historical Disasters in India by Type'
                },
                tooltip: {
                    callbacks: {
                        label: function(context) {
                            return `${context.parsed.y} incidents`;
                        }
                    }
                }
            },
            scales: {
                y: {
                    beginAtZero: true,
                    title: {
                        display: true,
                        text: 'Number of Incidents'
                    },
                    ticks: {
                        precision: 0
                    }
                },
                x: {
                    title: {
                        display: true,
                        text: 'Disaster Type'
                    }
                }
            }
        }
    });
}

function initPredictionDistributionChart() {
    const ctx = document.getElementById('predictionDistributionChart');
    if (!ctx) return;
    
    // Get all city dropdown elements
    const citySelectors = document.querySelectorAll('.city-selector');
    let selectedCities = [];
    
    // If there are city selectors, get the selected cities
    if (citySelectors.length > 0) {
        selectedCities = Array.from(citySelectors).map(select => select.value);
    } else {
        // If no selectors, use default cities
        selectedCities = [
            "Mumbai", "Delhi", "Bangalore", "Chennai", "Kolkata"
        ];
    }
    
    // Show loading indicator
    document.getElementById('prediction-chart-loading').classList.remove('d-none');
    
    // Create promises for fetching prediction data for each city
    const predictionPromises = selectedCities.map(city => {
        return fetch(`/api/disasters/predictions/${city}`)
            .then(response => {
                if (!response.ok) {
                    throw new Error(`Prediction data fetch failed for ${city}`);
                }
                return response.json();
            })
            .then(data => {
                return {
                    city: city,
                    predictions: data
                };
            })
            .catch(error => {
                console.error(`Error fetching prediction data for ${city}:`, error);
                return {
                    city: city,
                    predictions: []
                };
            });
    });
    
    // When all predictions are fetched
    Promise.all(predictionPromises)
        .then(results => {
            // Hide loading indicator
            document.getElementById('prediction-chart-loading').classList.add('d-none');
            
            // Process the prediction data
            const chartData = processPredictionData(results);
            
            // Create the chart
            createPredictionDistributionChart(ctx, chartData);
        })
        .catch(error => {
            console.error('Error fetching prediction data:', error);
            // Hide loading indicator
            document.getElementById('prediction-chart-loading').classList.add('d-none');
            // Show error message
            document.getElementById('prediction-chart-error').classList.remove('d-none');
            document.getElementById('prediction-chart-error').textContent = 'Failed to load prediction data. Please try again later.';
        });
}

function processPredictionData(cityPredictions) {
    // Collect disaster types across all cities
    const allDisasterTypes = new Set();
    cityPredictions.forEach(cityData => {
        cityData.predictions.forEach(prediction => {
            allDisasterTypes.add(prediction.disaster_type);
        });
    });
    
    const disasterTypes = Array.from(allDisasterTypes);
    const cities = cityPredictions.map(cityData => cityData.city);
    
    // Initialize data structure
    const datasets = disasterTypes.map((type, index) => {
        return {
            label: type,
            data: new Array(cities.length).fill(0),
            backgroundColor: getColorForDisasterType(type),
            stack: 'Stack 0'
        };
    });
    
    // Fill in the data
    cityPredictions.forEach((cityData, cityIndex) => {
        cityData.predictions.forEach(prediction => {
            const typeIndex = disasterTypes.indexOf(prediction.disaster_type);
            if (typeIndex !== -1) {
                // Use the probability value (0-1)
                datasets[typeIndex].data[cityIndex] = prediction.probability;
            }
        });
    });
    
    return {
        labels: cities,
        datasets: datasets
    };
}

function createPredictionDistributionChart(ctx, data) {
    new Chart(ctx, {
        type: 'bar',
        data: data,
        options: {
            responsive: true,
            plugins: {
                title: {
                    display: true,
                    text: 'Disaster Risk Distribution by City'
                },
                tooltip: {
                    callbacks: {
                        label: function(context) {
                            return `${context.dataset.label}: ${Math.round(context.parsed.y * 100)}% risk`;
                        }
                    }
                }
            },
            scales: {
                x: {
                    title: {
                        display: true,
                        text: 'City'
                    }
                },
                y: {
                    stacked: true,
                    title: {
                        display: true,
                        text: 'Risk Probability (0-1)'
                    },
                    max: 1
                }
            }
        }
    });
}

function getColorForDisasterType(type) {
    // Color mapping for different disaster types
    const colorMap = {
        'Flood': 'rgba(54, 162, 235, 0.8)',
        'Cyclone': 'rgba(75, 192, 192, 0.8)',
        'Drought': 'rgba(255, 205, 86, 0.8)',
        'Earthquake': 'rgba(201, 203, 207, 0.8)',
        'Landslide': 'rgba(153, 102, 255, 0.8)',
        'Tsunami': 'rgba(54, 162, 235, 0.8)',
        'Heat Wave': 'rgba(255, 99, 132, 0.8)',
        'Cold Wave': 'rgba(54, 162, 235, 0.8)',
        'Urban Flooding': 'rgba(54, 162, 235, 0.6)',
        'Forest Fire': 'rgba(255, 159, 64, 0.8)'
    };
    
    return colorMap[type] || 'rgba(100, 100, 100, 0.8)';
}
