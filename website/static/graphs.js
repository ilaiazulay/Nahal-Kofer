document.addEventListener('DOMContentLoaded', function() {
    const byYear = document.getElementById('byYear');
    const byDateRange = document.getElementById('byDateRange');
    const yearInput = document.getElementById('year');
    const startDate = document.getElementById('startDate');
    const endDate = document.getElementById('endDate');
    const optionsSelect = document.getElementById("options");
    const graphTitle = document.getElementById("graphTitle"); // Assuming there's an element to display the title
    const precipitationTitle = document.getElementById("precipitationTitle"); // Assuming there's an element to display the title
    const MinMaxTitle = document.getElementById("MinMaxTitle"); // Assuming there's an element to display the title

    function updateVisibility() {
        if (byYear.checked) {
            yearInput.parentElement.style.display = 'block';
            startDate.parentElement.style.display = 'none';
            endDate.parentElement.style.display = 'none';
            optionsSelect.style.display = 'block';
        } else if (byDateRange.checked) {
            yearInput.parentElement.style.display = 'none';
            startDate.parentElement.style.display = 'block';
            endDate.parentElement.style.display = 'block';
            optionsSelect.style.display = 'block';
        } else {
            optionsSelect.style.display = 'none';
        }
    }

    byYear.addEventListener('change', updateVisibility);
    byDateRange.addEventListener('change', updateVisibility);

    optionsSelect.addEventListener("change", function() {
        var selectedOption = this.value;
        var payload = {
            option: selectedOption
        };

        if (byYear.checked) {
            if (!yearInput.value) {
                alert("You have to pick a year.");
                return;
            }
            payload.dateData = { year: yearInput.value };
            var startDateValue = `${yearInput.value}-01-01`;
            var endDateValue = `${yearInput.value}-12-31`;
            fetchPrecipitationData(startDateValue, endDateValue);
        } else if (byDateRange.checked) {
            if (!startDate.value || !endDate.value) {
                alert("You have to pick both a start date and an end date.");
                return;
            }
            fetchPrecipitationData(startDate.value, endDate.value);
            payload.dateData = {
                startDate: startDate.value,
                endDate: endDate.value
            };
        } else {
            alert("Please select a date filtering option.");
            return;
        }

        // Fetch the graph data and the min/max values
        fetch('/get_graph_data', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(payload)
        })
        .then(response => response.json())
        .then(data => {
            renderGraph(data, selectedOption);
            fetchMinMaxData(payload);  // Fetch and display min/max data
        })
        .catch(error => {
            console.error('Error fetching graph data:', error);
        });
    });


function renderGraph(data, option) {
    var ctx = document.getElementById('graph').getContext('2d');

    if (window.myChart) {
        window.myChart.destroy(); // Destroy the existing chart instance if exists
    }

    // Update the graph title dynamically based on the selected option
    if(graphTitle) {
        graphTitle.textContent = `${option}`;
    }

    // Prepare datasets: Each location gets its own dataset
    var datasets = data.labels.map((location, index) => ({
        label: location, // Each location is a separate dataset
        data: [data.values[index]], // Wrap in array to match the expected data structure
        backgroundColor: generateBackgroundColor(index), // Function to generate color
        borderColor: generateBorderColor(index), // Function to generate border color
        borderWidth: 1
    }));

    window.myChart = new Chart(ctx, {
        type: 'bar', // Assuming bar type graph
        data: {
            labels: ['Average'], // Common label for all datasets
            datasets: datasets
        },
        options: {
            scales: {
                x: {
                    title: {
                        display: true,
                        text: 'Parameter'
                    }
                },
                y: {
                    beginAtZero: true,
                    title: {
                        display: true,
                        text: 'Value'
                    }
                }
            },
            plugins: {
                legend: {
                    display: true,
                    position: 'top'
                }
            },
            responsive: true
        }
    });
}

function generateBackgroundColor(index) {
    const colors = [
        'rgba(54, 162, 235, 0.5)',  // Blue
        'rgba(255, 99, 132, 0.5)',   // Red
        'rgba(75, 192, 192, 0.5)',   // Green
        'rgba(255, 206, 86, 0.5)',   // Yellow
        'rgba(153, 102, 255, 0.5)',  // Purple
        'rgba(255, 159, 64, 0.5)'    // Orange
    ];
    return colors[index % colors.length];
}

function generateBorderColor(index) {
    const colors = [
        'rgba(54, 162, 235, 1)',     // Blue
        'rgba(255, 99, 132, 1)',     // Red
        'rgba(75, 192, 192, 1)',     // Green
        'rgba(255, 206, 86, 1)',     // Yellow
        'rgba(153, 102, 255, 1)',    // Purple
        'rgba(255, 159, 64, 1)'      // Orange
    ];
    return colors[index % colors.length];
}



    function fetchMinMaxData(payload) {
    fetch('/get_min_max', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify(payload)
    })
    .then(response => response.json())
    .then(data => {
        displayMinMax(data);
    })
    .catch(error => {
        console.error('Error fetching min/max data:', error);
    });
}

function displayMinMax(data) {
    const minMaxContainer = document.getElementById('minMaxValues');
    minMaxContainer.innerHTML = ''; // Clear previous entries

    if(MinMaxTitle) {
        MinMaxTitle.textContent = `Minimum and Maximum Values by Location`; // Set the graph title dynamically
    }

    const table = document.createElement('table');
    table.classList.add('min-max-table');

    // Create table header
    const headerRow = document.createElement('tr');
    const locationHeader = document.createElement('th');
    locationHeader.textContent = 'Location';
    const minHeader = document.createElement('th');
    minHeader.textContent = 'Minimum';
    const maxHeader = document.createElement('th');
    maxHeader.textContent = 'Maximum';
    headerRow.appendChild(locationHeader);
    headerRow.appendChild(minHeader);
    headerRow.appendChild(maxHeader);
    table.appendChild(headerRow);

    // Create table rows for each location
    data.labels.forEach((location, index) => {
        const min = data.mins[index];
        const max = data.maxs[index];
        const row = document.createElement('tr');
        const locationCell = document.createElement('td');
        locationCell.textContent = location;
        const minCell = document.createElement('td');
        minCell.textContent = min;
        const maxCell = document.createElement('td');
        maxCell.textContent = max;
        row.appendChild(locationCell);
        row.appendChild(minCell);
        row.appendChild(maxCell);
        table.appendChild(row);
    });

    minMaxContainer.appendChild(table);
}

function fetchPrecipitationData(startDate, endDate) {
    const token = 'EhbOAoVcydnYoYpiFFwDAFzfqNVJcNfW'; // NOAA API token
    const stationId = 'GHCND:USW00094728'; // Example station ID for Tel Aviv, replace with actual ID if needed
    const datasetId = 'GHCND'; // Global Historical Climatology Network Daily
    const dataTypeId = 'PRCP'; // Data type ID for precipitation
    const url = `https://www.ncdc.noaa.gov/cdo-web/api/v2/data?datasetid=${datasetId}&datatypeid=${dataTypeId}&stationid=${stationId}&startdate=${startDate}&enddate=${endDate}&units=metric&limit=1000`;

    fetch(url, {
        headers: {
            'token': token
        }
    })
    .then(response => {
        if (!response.ok) {
            throw new Error('Network response was not ok');
        }
        return response.json();
    })
    .then(data => {
        console.log('Precipitation data:', data);
        displayPrecipitationGraph(data);
    })
    .catch(error => {
        console.error('Error fetching precipitation data:', error);
    });
}


function displayPrecipitationGraph(data) {
    var labels = [];
    var precipitationData = [];

    if(precipitationTitle) {
        precipitationTitle.textContent = `Precipitation Data`; // Set the graph title dynamically
    }

    if (data && data.results) {
        data.results.forEach(result => {
            labels.push(result.date); // 'date' might need to be formatted properly
            precipitationData.push(result.value); // Assuming 'value' is the precipitation amount
        });
    }

    var ctx = document.getElementById('precipitationGraph').getContext('2d');
    if (window.precipitationChart) {
        window.precipitationChart.destroy();
    }

    window.precipitationChart = new Chart(ctx, {
        type: 'line',
        data: {
            labels: labels,
            datasets: [{
                label: 'Daily Precipitation (mm)',
                data: precipitationData,
                backgroundColor: 'rgba(66, 135, 245, 0.2)',
                borderColor: 'rgba(66, 135, 245, 1)',
                borderWidth: 1,
                pointRadius: 2,
                fill: true
            }]
        },
        options: {
            scales: {
                x: {
                    title: {
                        display: true,
                        text: 'Date'
                    }
                },
                y: {
                    beginAtZero: true,
                    title: {
                        display: true,
                        text: 'Precipitation (mm)'
                    }
                }
            },
            plugins: {
                legend: {
                    display: true,
                    position: 'top'
                }
            },
            responsive: true,
            maintainAspectRatio: false
        }
    });
}


});
