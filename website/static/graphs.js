document.addEventListener('DOMContentLoaded', function() {
    const byYear = document.getElementById('byYear');
    const byDateRange = document.getElementById('byDateRange');
    const yearInput = document.getElementById('year');
    const startDate = document.getElementById('startDate');
    const endDate = document.getElementById('endDate');
    const optionsSelect = document.getElementById("options");
    const graphTitle = document.getElementById("graphTitle"); // Assuming there's an element to display the title

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
        } else if (byDateRange.checked) {
            if (!startDate.value || !endDate.value) {
                alert("You have to pick both a start date and an end date.");
                return;
            }
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
            window.myChart.destroy();
        }

        if(graphTitle) {
            graphTitle.textContent = `${option}`; // Set the graph title dynamically
        }

        window.myChart = new Chart(ctx, {
            type: 'bar',
            data: {
                labels: data.labels,
                datasets: [{
                    label: data.labels,
                    data: data.values,
                    backgroundColor: 'rgba(54, 162, 235, 0.5)',
                    borderColor: 'rgba(54, 162, 235, 1)',
                    borderWidth: 1
                }]
            },
            options: {
                scales: {
                    x: {
                        title: {
                            display: true,
                            text: 'Location'
                        }
                    },
                    y: {
                        beginAtZero: true,
                        title: {
                            display: true,
                            text: 'Average Value'
                        }
                    }
                },
                plugins: {
                    legend: {
                        display: true,
                        position: 'top',
                        labels: {
                            color: 'rgb(54, 162, 235)' // Ensure this matches your design
                        }
                    }
                }
            }
        });
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


});
