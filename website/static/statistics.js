document.getElementById("options1").addEventListener("change", function() {
  var selectedOption1 = this.value;
  console.log("Selected option1:", selectedOption1);

  document.getElementById("options2").addEventListener("change", function() {
    var selectedOption2 = this.value;
    console.log("Selected option2:", selectedOption2);

    // Fetch data from the backend based on the selected options
    fetch('/get_correlation_graph_data', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ option1: selectedOption1, option2: selectedOption2 })
    })
    .then(response => response.json())
    .then(data => {
      console.log("Graph data:", data);
      renderGraph(data, selectedOption2);
    })
    .catch(error => {
      console.error('Error fetching graph data:', error);
      // You can add code here to display an error message to the user
    });
  });
});

// Function to render the graph
function renderGraph(data, selectedOption2) {
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
        label: document.getElementById("options1").value,
        data: data.values1,
        backgroundColor: 'rgba(54, 162, 235, 0.2)', // Example background color
        borderColor: 'rgba(54, 162, 235, 1)', // Example border color
        borderWidth: 1 // Example border width
      },
      {
        label: document.getElementById("options2").value,
        data: data.values2,
        backgroundColor: 'rgba(255, 99, 132, 0.2)', // Example background color
        borderColor: 'rgba(255, 99, 132, 1)', // Example border color
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
