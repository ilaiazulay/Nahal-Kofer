function deleteShift(shiftId) {
    fetch('/delete-shift', {
        method: 'POST',
        body: JSON.stringify({ shiftId: shiftId }),
    }).then((_res) => {
        window.location.href = "/";
    });
}