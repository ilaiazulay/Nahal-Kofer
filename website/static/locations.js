function toggleForm(id) {
  const addButton = document.getElementById('add-location-btn');
  const form = document.getElementById('add-location-form');
  if (id === 'add-location') {
    if (form.style.display === 'none' || form.style.display === '') {
      form.style.display = 'block';
      addButton.style.display = 'none'; // Hide the add button
    } else {
      form.style.display = 'none';
      addButton.style.display = 'block'; // Show the add button again
    }
  } else {
    const editButton = document.getElementById('edit-button-' + id);
    const name = document.getElementById('name-' + id);
    const editForm = document.getElementById('edit-form-' + id);
    const deleteButton = document.querySelector('#location-' + id + ' .delete-btn');
    const input = editForm.querySelector('input[name="location_name"]'); // Get the input field for location name
    if (editForm.style.display === 'none' || editForm.style.display === '') {
      editForm.style.display = 'block';
      name.style.display = 'none';
      editButton.style.display = 'none';
      input.value = name.textContent; // Set the input field value to the current location name
      if (deleteButton) deleteButton.style.display = 'none';
    } else {
      editForm.style.display = 'none';
      name.style.display = '';
      editButton.style.display = 'block';
      if (deleteButton) deleteButton.style.display = 'block';
    }
  }
}

function cancelAddLocation() {
  const form = document.getElementById('add-location-form');
  const addButton = document.getElementById('add-location-btn');
  form.style.display = 'none';
  addButton.style.display = 'block';
}

function cancelEdit(id) {
  toggleForm(id);
}

document.getElementById('add-location-btn').addEventListener('click', function() {
  toggleForm('add-location');
});