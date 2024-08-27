document.addEventListener("DOMContentLoaded", function() {
    const apiKey = '87a8064c9b4357fcf99ad406e6e63f02'; // Replace 'YOUR_API_KEY' with your actual API key
    const city = 'Tel-Aviv';
    const lon = 34.824783;
    const lat = 32.068424;
    const currentWeatherUrl = `https://api.openweathermap.org/data/2.5/weather?q=${city}&appid=${apiKey}`;
    const forecastUrl = `https://api.openweathermap.org/data/2.5/forecast?lat=${lat}&lon=${lon}&appid=${apiKey}`;

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
            displayDailyForecast(data.list);
        })
        .catch(error => {
            console.error('Error fetching forecast data:', error);
            alert('Error fetching forecast data. Please try again.');
        });
});

function displayWeather(data) {
    const weatherInfoDiv = document.getElementById('weather-info');
    const weatherIcon = document.getElementById('weather-icon');

    const cityName = data.name;
    const description = data.weather[0].description;
    const iconCode = data.weather[0].icon;
    const iconUrl = `https://openweathermap.org/img/wn/${iconCode}@4x.png`;
    const precipitation = data.rain ? data.rain['1h'] : 0; // 1 hour precipitation data

    const weatherHtml = `<p>${cityName}</p><p>${description}</p><p>Precip: ${precipitation} mm</p>`;

    weatherInfoDiv.innerHTML = weatherHtml;
    weatherIcon.src = iconUrl;
    weatherIcon.alt = description;
}

function displayHourlyForecast(hourlyData) {
    const hourlyForecastDiv = document.getElementById('hourly-forecast');
    hourlyForecastDiv.innerHTML = ''; // Clear previous content

    const next24Hours = hourlyData.slice(0, 8); // Display the next 24 hours (3-hour intervals)

    next24Hours.forEach(item => {
        const dateTime = new Date(item.dt * 1000); // Convert timestamp to milliseconds
        const hour = dateTime.getHours();
        const precipitation = item.rain ? item.rain['3h'] : 0; // 3 hour precipitation data
        const iconCode = item.weather[0].icon;
        const iconUrl = `https://openweathermap.org/img/wn/${iconCode}.png`;

        const hourlyItemHtml = `<div class="hourly-item"><span>${hour}:00</span><img src="${iconUrl}" alt="Hourly Weather Icon"><span>Precip: ${precipitation} mm</span></div>`;

        hourlyForecastDiv.innerHTML += hourlyItemHtml;
    });
}

function displayDailyForecast(hourlyData) {
    const dailyForecastDiv = document.getElementById('daily-forecast');
    dailyForecastDiv.innerHTML = ''; // Clear previous content

    const days = {};

    hourlyData.forEach(item => {
        const date = new Date(item.dt * 1000).toDateString(); // Get date string
        const precipitation = item.rain ? item.rain['3h'] : 0; // 3 hour precipitation data
        const iconCode = item.weather[0].icon;

        if (!days[date]) {
            days[date] = {
                totalPrecipitation: precipitation,
                icon: iconCode,
                count: 1
            };
        } else {
            days[date].totalPrecipitation += precipitation;
            days[date].count++;
        }
    });

    Object.keys(days).forEach(date => {
        const day = days[date];
        const iconUrl = `https://openweathermap.org/img/wn/${day.icon}.png`;
        const averagePrecipitation = (day.totalPrecipitation / day.count).toFixed(2);

        const dailyItemHtml = `<div class="daily-item"><span>${date}</span><img src="${iconUrl}" alt="Daily Weather Icon"><span>Avg. Precip: ${averagePrecipitation} mm</span></div>`;

        dailyForecastDiv.innerHTML += dailyItemHtml;
    });
}

function displayRainForecast(hourlyData) {
    const hourlyForecastDiv = document.getElementById('rain-forecast');
    const rainForecast = {}; // Object to store rain forecast for each day

    hourlyData.forEach(item => {
        const dateTime = new Date(item.dt * 1000); // Convert timestamp to milliseconds
        const date = dateTime.toDateString(); // Get the date without the time
        const hour = dateTime.getHours();
        const precipitation = item.rain ? item.rain['3h'] : 0; // 3 hour precipitation data

        if (!rainForecast[date]) {
            rainForecast[date] = [];
        }
        rainForecast[date].push({ hour, precipitation });
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
        rainForecastHTML += `<p>${date}: ${hours.length} hours of rain expected, avg. precip.: ${averagePrecipitation} mm</p>`;
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
        // Fetch distance sensor data
        const distanceResponse = await fetch('/get_distance_sensor_data');
        const distanceData = await distanceResponse.json();
        console.log(distanceData);
        let distance = distanceData.distance;
        if (distance !== undefined) {
            if (distance == 1000)
            {
                document.getElementById('reading').innerHTML = 'Lost Connection';
            }
            else
            {
                distance = parseFloat(distance).toFixed(1);  // Format to one decimal place
                distance -= 20;
                if(distance < 0)
                {
                    distance = 0;
                }
                distance = distance.toFixed(1);
                document.getElementById('reading').innerHTML = `${distance} cm`;
            }
        } else {
            document.getElementById('reading').innerHTML = 'Lost Connection';
        }

        const floodAlertElement = document.getElementById('floodAlert');
        if (distance <= 7) {
            floodAlertElement.style.display = 'block'; // Show flood alert
        } else {
            floodAlertElement.style.display = 'none'; // Hide flood alert
        }

        // Fetch flow rate sensor data
        const flowRateResponse = await fetch('/get_flow_sensor_data');
        const flowRateData = await flowRateResponse.json();
        let flowRate = flowRateData.flow_rate;
        if (flowRate !== undefined) {
            if (flowRate == 1000)
            {
                document.getElementById('water_current_reading').innerHTML = 'Lost Connection';
            }
            else
            {
                flowRate = parseFloat(flowRate).toFixed(1);  // Format to one decimal place
                document.getElementById('water_current_reading').innerHTML = `${flowRate} L/min`;
            }
        } else {
            document.getElementById('water_current_reading').innerHTML = 'Lost Connection';
        }

        // Fetch ph sensor data
        const phResponse = await fetch('/get_ph_sensor_data');
        const phData = await phResponse.json();
        let ph = phData.ph_value;
        if (ph !== undefined) {
            if (ph == 1000)
            {
                document.getElementById('ph_reading').innerHTML = 'Lost Connection';
            }
            else
            {
                ph = parseFloat(ph).toFixed(1);  // Format to one decimal place
                document.getElementById('ph_reading').innerHTML = `${ph}`;
            }
        } else {
            document.getElementById('ph_reading').innerHTML = 'Lost Connection';
        }

    } catch (error) {
        console.error('Error fetching sensor data:', error);
    }
}

setInterval(updateSensorData, 1000);  // Update every second
