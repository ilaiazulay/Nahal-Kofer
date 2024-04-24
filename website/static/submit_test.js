function toggleReadOnly(fieldId, buttonId) {
    var field = document.getElementById(fieldId);
    var button = document.getElementById(buttonId);
    field.readOnly = !field.readOnly;
    button.style.display = 'none';  // Hide the edit button after clicked
}