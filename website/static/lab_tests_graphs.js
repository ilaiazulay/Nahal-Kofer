document.addEventListener('DOMContentLoaded', function() {
    const startDate = document.getElementById('startDate');
    const endDate = document.getElementById('endDate');
    const optionsSelect = document.getElementById("options");
    const graphTitle = document.getElementById("graphTitle");
    const precipitationTitle = document.getElementById("precipitationTitle");
    const MinMaxTitle = document.getElementById("MinMaxTitle");
    const barChartRadio = document.getElementById('barChart');
    const lineChartRadio = document.getElementById('lineChart');

    optionsSelect.addEventListener("change", fetchData);

    barChartRadio.addEventListener('change', fetchData);
    lineChartRadio.addEventListener('change', fetchData);

    function fetchData() {
        var selectedOption = optionsSelect.value;
        var payload = {
            option: selectedOption
        };

        if (!startDate.value || !endDate.value) {
            alert("You have to pick both a start date and an end date.");
            return;
        }
        fetchPrecipitationData(startDate.value, endDate.value);
        payload.dateData = {
            startDate: startDate.value,
            endDate: endDate.value
        };

        if (barChartRadio.checked) {
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
                fetchMinMaxData(payload);
            })
            .catch(error => {
                console.error('Error fetching graph data:', error);
            });
        } else if (lineChartRadio.checked) {
            fetch('/get_line_graph_data', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(payload)
            })
            .then(response => response.json())
            .then(data => {
                renderLineGraph(data);
                fetchMinMaxData(payload);
            })
            .catch(error => {
                console.error('Error fetching line graph data:', error);
            });
        }
    }

    function renderGraph(data, option) {
        var ctx = document.getElementById('graph').getContext('2d');

        if (window.myChart) {
            window.myChart.destroy();
        }

        if(graphTitle) {
            graphTitle.textContent = `${option}`;
        }

        var datasets = data.labels.map((location, index) => ({
            label: location,
            data: [data.values[index]],
            backgroundColor: generateBackgroundColor(index),
            borderColor: generateBorderColor(index),
            borderWidth: 1
        }));

        window.myChart = new Chart(ctx, {
            type: 'bar',
            data: {
                labels: ['Average'],
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

    function renderLineGraph(data) {
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
                            text: 'Value'
                        }
                    }
                },
                plugins: {
                    legend: {
                        display: true,
                        position: 'top'
                    },
                    zoom: {
                        pan: {
                            enabled: true,
                            mode: 'x',
                        },
                        zoom: {
                            wheel: {
                                enabled: true,
                            },
                            pinch: {
                                enabled: true
                            },
                            mode: 'x',
                        }
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
        minMaxContainer.innerHTML = '';

        if(MinMaxTitle) {
            MinMaxTitle.textContent = `Minimum and Maximum Values by Location`;
        }

        const table = document.createElement('table');
        table.classList.add('min-max-table');

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
                    },
                    zoom: {
                        pan: {
                            enabled: true,
                            mode: 'x',
                        },
                        zoom: {
                            wheel: {
                                enabled: true,
                            },
                            pinch: {
                                enabled: true
                            },
                            mode: 'x',
                        }
                    }
                },
                responsive: true,
                maintainAspectRatio: false
            }
        });
    }
});
