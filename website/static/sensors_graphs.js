document.addEventListener('DOMContentLoaded', function() {
    const byYear = document.getElementById('byYear');
    const byDateRange = document.getElementById('byDateRange');
    const yearInput = document.getElementById('year');
    const startDate = document.getElementById('startDate');
    const endDate = document.getElementById('endDate');
    const optionsSelect = document.getElementById("options");
    const graphTitle = document.getElementById("graphTitle");
    const precipitationTitle = document.getElementById("precipitationTitle");

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

    optionsSelect.addEventListener("change", fetchData);

    function fetchData() {
        var selectedOption = optionsSelect.value;
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

        fetch('/get_sensors_graph_data', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(payload)
        })
        .then(response => response.json())
        .then(data => {
            renderGraph(data, selectedOption);
        })
        .catch(error => {
            console.error('Error fetching graph data:', error);
        });
    }

    function renderGraph(data, selectedOption) {
        var ctx = document.getElementById('graph').getContext('2d');

        if (window.myChart) {
            window.myChart.destroy();
        }

        var datasets = Object.keys(data).map((location, index) => ({
            label: location,
            data: data[location].dates.map((date, i) => ({
                x: date,
                y: data[location].values[i]
            })),
            backgroundColor: generateBackgroundColor(index),
            borderColor: generateBorderColor(index),
            borderWidth: 1,
            fill: false
        }));

        window.myChart = new Chart(ctx, {
            type: 'line',
            data: {
                datasets: datasets
            },
            options: {
                scales: {
                    x: {
                        type: 'time',
                        title: {
                            display: true,
                            text: 'Date'
                        }
                    },
                    y: {
                        beginAtZero: true,
                        title: {
                            display: true,
                            text: selectedOption
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
            'rgba(54, 162, 235, 0.5)',
            'rgba(255, 99, 132, 0.5)',
            'rgba(75, 192, 192, 0.5)',
            'rgba(255, 206, 86, 0.5)',
            'rgba(153, 102, 255, 0.5)',
            'rgba(255, 159, 64, 0.5)'
        ];
        return colors[index % colors.length];
    }

    function generateBorderColor(index) {
        const colors = [
            'rgba(54, 162, 235, 1)',
            'rgba(255, 99, 132, 1)',
            'rgba(75, 192, 192, 1)',
            'rgba(255, 206, 86, 1)',
            'rgba(153, 102, 255, 1)',
            'rgba(255, 159, 64, 1)'
        ];
        return colors[index % colors.length];
    }

    function fetchPrecipitationData(startDate, endDate) {
        const token = 'EhbOAoVcydnYoYpiFFwDAFzfqNVJcNfW';
        const stationId = 'GHCND:USW00094728';
        const datasetId = 'GHCND';
        const dataTypeId = 'PRCP';
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
            precipitationTitle.textContent = `Precipitation Data`;
        }

        if (data && data.results) {
            data.results.forEach(result => {
                labels.push(result.date);
                precipitationData.push(result.value);
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
