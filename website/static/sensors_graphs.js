document.addEventListener('DOMContentLoaded', function() {
    const startDate = document.getElementById('startDate');
    const endDate = document.getElementById('endDate');
    const optionsSelect = document.getElementById("options");
    const graphTitle = document.getElementById("graphTitle");
    const precipitationTitle = document.getElementById("precipitationTitle");
    const zoomSlider = document.getElementById('zoomSlider');
    const zoomSliderContainer = document.getElementById('zoomSliderContainer');

    optionsSelect.addEventListener("change", function() {
        if (optionsSelect.value) {
            fetchData();
        }
    });

    startDate.addEventListener("change", function() {
        if (optionsSelect.value) {
            fetchData();
        }
    });

    endDate.addEventListener("change", function() {
        if (optionsSelect.value) {
            fetchData();
        }
    });

    zoomSlider.addEventListener('input', handleZoom);

    function fetchData() {
        var selectedOption = optionsSelect.value;

        if (!selectedOption) {
            alert("You have to pick a parameter.");
            return;
        }

        if (!startDate.value || !endDate.value) {
            alert("You have to pick both a start date and an end date.");
            return;
        }

        var payload = {
            option: selectedOption,
            dateData: {
                startDate: startDate.value,
                endDate: endDate.value
            }
        };

        fetchPrecipitationData(startDate.value, endDate.value);

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
                        time: {
                            unit: 'day'
                        },
                        title: {
                            display: true,
                            text: 'Date'
                        },
                        min: startDate.value,
                        max: endDate.value
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
                    },
                    zoom: {
                        pan: {
                            enabled: false,
                        },
                        zoom: {
                            wheel: {
                                enabled: false,
                            },
                            pinch: {
                                enabled: false
                            },
                            mode: 'x',
                            onZoomComplete: syncCharts
                        }
                    }
                },
                responsive: true
            }
        });
    }

    function handleZoom(event) {
        const zoomLevel = event.target.value;
        const min = parseInt(zoomSlider.min);
        const max = parseInt(zoomSlider.max);
        const scale = 1 + (zoomLevel - min) / (max - min) * 9;

        zoomChart(window.myChart, scale);
        zoomChart(window.precipitationChart, scale);
    }

    function zoomChart(chart, scale) {
        if (!chart) return;
        const { min: initialMin, max: initialMax } = chart.scales.x.originalRange || {
            min: chart.scales.x.min,
            max: chart.scales.x.max
        };

        if (!chart.scales.x.originalRange) {
            chart.scales.x.originalRange = { min: initialMin, max: initialMax };
        }

        const range = initialMax - initialMin;
        const newRange = range / scale;
        const newMin = initialMin + (range - newRange) / 2;
        const newMax = initialMax - (range - newRange) / 2;

        chart.scales.x.options.min = newMin;
        chart.scales.x.options.max = newMax;
        chart.update();
    }

    function syncCharts({ chart }) {
        const xScale = chart.scales.x;
        const newMin = xScale.min;
        const newMax = xScale.max;

        if (window.precipitationChart && window.precipitationChart !== chart) {
            window.precipitationChart.scales.x.options.min = newMin;
            window.precipitationChart.scales.x.options.max = newMax;
            window.precipitationChart.update();
        }

        if (window.myChart && window.myChart !== chart) {
            window.myChart.scales.x.options.min = newMin;
            window.myChart.scales.x.options.max = newMax;
            window.myChart.update();
        }
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
        const loadingSpinner = document.getElementById('loadingSpinner');
        const precipitationGraph = document.getElementById('precipitationGraph');

        // Clear the previous precipitation graph
        if (window.precipitationChart) {
            window.precipitationChart.destroy();
        }
        precipitationGraph.getContext('2d').clearRect(0, 0, precipitationGraph.width, precipitationGraph.height);

        loadingSpinner.classList.remove('hidden');

        // Send a request to the Flask backend to fetch precipitation data
        fetch('/get_precipitation_data', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                startDate: startDate,
                endDate: endDate
            })
        })
        .then(response => response.json())
        .then(data => {
            if (data.error) {
                throw new Error(data.error);
            }
            displayPrecipitationGraph(data, startDate, endDate);
            loadingSpinner.classList.add('hidden');
        })
        .catch(error => {
            console.error('Error fetching precipitation data:', error);
            setTimeout(() => {
                fetchPrecipitationData(startDate, endDate);
            }, 3000); // Retry after 3 seconds
        });
    }


    function displayPrecipitationGraph(data, startDate, endDate) {
        var labels = [];
        var precipitationData = [];

        if (precipitationTitle) {
            precipitationTitle.textContent = `Precipitation Data`;
        }

        if (data && data.results) {
            data.results.forEach(result => {
                labels.push(result.date.split('T')[0]); // Only display the date
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
                        type: 'time',
                        time: {
                            unit: 'day' // Show only the date on the x-axis
                        },
                        title: {
                            display: true,
                            text: 'Date'
                        },
                        min: startDate,
                        max: endDate
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
                            enabled: false,
                        },
                        zoom: {
                            wheel: {
                                enabled: false,
                            },
                            pinch: {
                                enabled: false
                            },
                            mode: 'x',
                            onZoomComplete: syncCharts
                        }
                    }
                },
                responsive: true,
                maintainAspectRatio: false
            }
        });
    }
});
