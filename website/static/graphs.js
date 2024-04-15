document.getElementById("options").addEventListener("change", function() {
var selectedOption = this.value;
console.log("Selected option:", selectedOption);

// Fetch data from the backend based on the selected option
fetch('/get_graph_data', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
  },
  body: JSON.stringify({ option: selectedOption })
})
.then(response => response.json())
.then(data => {
  console.log("Graph data:", data);
  renderGraph(data);
})
.catch(error => {
  console.error('Error fetching graph data:', error);
});
});

// Function to render the graph
function renderGraph(data) {
    var ctx = document.getElementById('graph').getContext('2d');

    // Destroy existing Chart instance if it exists
    if (window.myChart) {
        window.myChart.destroy();
    }

    window.myChart = new Chart(ctx, {
        type: 'line', // Or 'bar' or any other type
        data: {
            labels: data.labels,
            datasets: [{
                label: 'NTU Levels',
                data: data.values,
                backgroundColor: 'rgba(54, 162, 235, 0.2)',
                borderColor: 'rgba(54, 162, 235, 1)',
                borderWidth: 1
            }]
        },
        options: {
            scales: {
                x: {
                    type: 'time',
                    time: {
                        unit: 'day'
                    }
                },
                y: {
                    beginAtZero: true
                }
            },
            plugins: {
                zoom: {
                    zoom: {
                        wheel: {
                            enabled: true, // Enable zooming with mouse wheel
                        },
                        pinch: {
                            enabled: true // Enable zooming with pinch gesture
                        },
                        mode: 'x' // Allow zooming in the x direction
                    },
                    pan: {
                        enabled: true, // Enable panning
                        mode: 'x' // Allow panning in the x direction
                    }
                }
            }
        }
    });
}

