document.addEventListener("DOMContentLoaded", function() {
    // pH Gauge
    const phCtx = document.getElementById('phGauge').getContext('2d');
    const phGauge = new Chart(phCtx, {
        type: 'doughnut',
        data: {
            datasets: [{
                data: [ ph_average , 14 -  ph_average ],
                backgroundColor: [
                    '#36A2EB', // blue for actual value
                    '#f0f0f0' // gray for remaining part
                ]
            }]
        },
        options: {
            cutoutPercentage: 70, // hole in the middle
            rotation: -29 * Math.PI, // to start from top
            circumference: 58 * Math.PI, // to make it half circle
            legend: {
                display: false
            }
        }
    });

    // Hardness Gauge
    const hardnessCtx = document.getElementById('hardnessGauge').getContext('2d');
    const hardnessGauge = new Chart(hardnessCtx, {
        type: 'doughnut',
        data: {
            datasets: [{
                data: [ hardness_average , 14 -  hardness_average ],
                backgroundColor: [
                    '#FFCE56', // yellow for actual value
                    '#f0f0f0' // gray for remaining part
                ]
            }]
        },
        options: {
            cutoutPercentage: 70, // hole in the middle
            rotation: -29 * Math.PI, // to start from top
            circumference: 58 * Math.PI, // to make it half circle
            legend: {
                display: false
            }
        }
    });

    // TS Gauge
    const tsCtx = document.getElementById('tsGauge').getContext('2d');
    const tsGauge = new Chart(tsCtx, {
        type: 'doughnut',
        data: {
            datasets: [{
                data: [ ts_average , 14 -  ts_average ],
                backgroundColor: [
                    '#FF6384', // red for actual value
                    '#f0f0f0' // gray for remaining part
                ]
            }]
        },
        options: {
            cutoutPercentage: 70, // hole in the middle
            rotation: -29 * Math.PI, // to start from top
            circumference: 58 * Math.PI, // to make it half circle
            legend: {
                display: false
            }
        }
    });
});


// Weather API
document.addEventListener("DOMContentLoaded", function() {
    const apiKey = '87a8064c9b4357fcf99ad406e6e63f02';
    const city = 'Tel-Aviv';
    const lon = 34.824783;
    const lat = 32.068424;
    const currentWeatherUrl = 'https://api.openweathermap.org/data/2.5/weather?q=Tel-Aviv&appid=87a8064c9b4357fcf99ad406e6e63f02';
    const forecastUrl = 'https://api.openweathermap.org/data/2.5/forecast?lat=32.068424&lon=34.824783&appid=87a8064c9b4357fcf99ad406e6e63f02';

        fetch(currentWeatherUrl)
        .then(response => response.json())
        .then(data => {
            displayWeather(data);
        })
        .catch(error => {
            console.error('Error fetching current weather data:', error);
            alert('Error fetching current weather data. Please try again.');
        });

    fetch(forecastUrl)
        .then(response => response.json())
        .then(data => {
            displayHourlyForecast(data.list);
            displayRainForecast(data.list);
        })
        .catch(error => {
            console.error('Error fetching hourly forecast data:', error);
            alert('Error fetching hourly forecast data. Please try again.');
        });
});

function displayWeather(data) {
    const tempDivInfo = document.getElementById('temp-div');
    const weatherInfoDiv = document.getElementById('weather-info');
    const weatherIcon = document.getElementById('weather-icon');
    const hourlyForecastDiv = document.getElementById('hourly-forecast');

    // Clear previous content
    weatherInfoDiv.innerHTML = '';
    hourlyForecastDiv.innerHTML = '';
    tempDivInfo.innerHTML = '';

    if (data.cod === '404') {
        weatherInfoDiv.innerHTML = `<p>${data.message}</p>`;
    } else {
        const cityName = data.name;
        const temperature = Math.round(data.main.temp - 273.15); // Convert to Celsius
        const description = data.weather[0].description;
        const iconCode = data.weather[0].icon;
        const iconUrl = `https://openweathermap.org/img/wn/${iconCode}@4x.png`;

        const temperatureHTML = `
            <p>${temperature}°C</p>
        `;

        const weatherHtml = `
            <p>${cityName}</p>
            <p>${description}</p>
        `;

        tempDivInfo.innerHTML = temperatureHTML;
        weatherInfoDiv.innerHTML = weatherHtml;
        weatherIcon.src = iconUrl;
        weatherIcon.alt = description;

        showImage();
    }
}

function displayHourlyForecast(hourlyData) {
    const hourlyForecastDiv = document.getElementById('hourly-forecast');

    const next24Hours = hourlyData.slice(0, 8); // Display the next 24 hours (3-hour intervals)

    next24Hours.forEach(item => {
        const dateTime = new Date(item.dt * 1000); // Convert timestamp to milliseconds
        const hour = dateTime.getHours();
        console.log(hour)
        const temperature = Math.round(item.main.temp - 273.15); // Convert to Celsius
        console.log(temperature)
        const iconCode = item.weather[0].icon;
        console.log(iconCode);
        const iconUrl = `https://openweathermap.org/img/wn/${iconCode}.png`;

        const hourlyItemHtml = `
            <div class="hourly-item">
                <span>${hour}:00</span>
                <img src="${iconUrl}" alt="Hourly Weather Icon">
                <span>${temperature}°C</span>
            </div>
        `;

        hourlyForecastDiv.innerHTML += hourlyItemHtml;
    });
}

function displayRainForecast(hourlyData) {
    const hourlyForecastDiv = document.getElementById('rain-forecast');
    const rainForecast = {}; // Object to store rain forecast for each day

    hourlyData.forEach(item => {
        const dateTime = new Date(item.dt * 1000); // Convert timestamp to milliseconds
        const date = dateTime.toDateString(); // Get the date without the time
        const hour = dateTime.getHours();
        const temperature = Math.round(item.main.temp - 273.15); // Convert to Celsius
        const weatherDescription = item.weather[0].description;

        // Check if it's raining
        if (weatherDescription.includes('rain')) {
            if (!rainForecast[date]) {
                rainForecast[date] = [];
            }
            rainForecast[date].push({ hour, precipitation: item.rain ? item.rain['3h'] : 0 });
        }
    });

    // Create HTML for rain forecast paragraph
    let rainForecastHTML = '';

    // Iterate over rain forecast data and add to the HTML
    for (const [date, hours] of Object.entries(rainForecast)) {
        let totalPrecipitation = 0;
        hours.forEach(hourData => {
            totalPrecipitation += hourData.precipitation;
        });
        const averagePrecipitation = totalPrecipitation / hours.length;
        rainForecastHTML += `<p>${date}: ${hours.length} hours of rain expected, average precipitation: ${averagePrecipitation} mm</p>`;
    }

    // Update the HTML content with rain forecast
    hourlyForecastDiv.innerHTML = rainForecastHTML;
}


function showImage() {
    const weatherIcon = document.getElementById('weather-icon');
    weatherIcon.style.display = 'block'; // Make the image visible once it's loaded
}

async function updateSensorData() {
    try {
        const response = await fetch('/get_sensor_data');
        console.log(response);
        const data = await response.json();
        document.getElementById('reading').innerHTML = data.distance + ' cm';
    } catch (error) {
        console.error('Error fetching sensor data:', error);
    }
}

setInterval(updateSensorData, 1000);  // Update every second