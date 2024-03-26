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
    type: 'line', // Change the chart type as needed (e.g., 'bar', 'pie', etc.)
    data: {
      labels: data.labels,
      datasets: [{
        label: document.getElementById("options").value,
        data: data.values,
        backgroundColor: 'rgba(54, 162, 235, 0.2)', // Example background color
        borderColor: 'rgba(54, 162, 235, 1)', // Example border color
        borderWidth: 1 // Example border width
      }]
    },
    options: {
      scales: {
        y: {
          beginAtZero: true
        }
      }
    }
  });
}
