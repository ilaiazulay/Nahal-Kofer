function deleteShift(shiftId) {
    fetch('/delete-shift', {
        method: 'POST',
        body: JSON.stringify({ shiftId: shiftId }),
    }).then((_res) => {
        window.location.href = "/";
    });
}

function confirmDelete(shiftId) {
    var confirmDelete = confirm("Are you sure you want to delete this shift?");
    if (confirmDelete) {
        deleteShift(shiftId);
    }
}