//function deleteShift(shiftId) {
//    fetch('/delete-shift', {
//        method: 'POST',
//        body: JSON.stringify({ shiftId: shiftId }),
//    }).then((_res) => {
//        window.location.href = "/";
//    });
//}
//
//function confirmDelete(shiftId) {
//    var confirmDelete = confirm("Are you sure you want to delete this shift?");
//    if (confirmDelete) {
//        deleteShift(shiftId);
//    }
//}

document.addEventListener('DOMContentLoaded', function() {
    var dropdownToggle = document.querySelector('.dropdown-toggle');
    var dropdownMenu = document.querySelector('.dropdown-menu');

    dropdownToggle.addEventListener('click', function(event) {
        handleDropdownToggle(event);
    });

    document.addEventListener('click', function(event) {
        if (!dropdownToggle.contains(event.target) && !dropdownMenu.contains(event.target)) {
            dropdownMenu.classList.remove('show');
            dropdownToggle.classList.remove('active');
        }
    });

    // Function to handle dropdown toggle
    function handleDropdownToggle(event) {
        // Prevent default action and event propagation
        event.preventDefault();
        event.stopPropagation();

        // Check if the dropdown is already shown
        var isDropdownVisible = dropdownMenu.classList.contains('show');

        // Check if the current path starts with '/graphs'
        var isGraphsPath = window.location.pathname.startsWith('/graphs');

        // Only toggle if the path is not '/graphs'
        if (!isGraphsPath) {
            // Toggle the visibility of the dropdown menu
            if (isDropdownVisible) {
                dropdownMenu.classList.remove('show');
                dropdownToggle.classList.remove('active');
                refreshDropdownComponent(); // Refresh component
            } else {
                dropdownMenu.classList.add('show');
                dropdownToggle.classList.add('active');
            }
        }
    }

    // Function to refresh the dropdown component
    function refreshDropdownComponent() {
        // Remove and re-add the element to refresh it
        var parent = dropdownToggle.parentNode;
        var newDropdownToggle = dropdownToggle.cloneNode(true);
        var newDropdownMenu = dropdownMenu.cloneNode(true);

        // Replace the old nodes with the new ones
        parent.replaceChild(newDropdownToggle, dropdownToggle);
        parent.replaceChild(newDropdownMenu, dropdownMenu);

        // Reassign the variables to the new elements
        dropdownToggle = newDropdownToggle;
        dropdownMenu = newDropdownMenu;

        // Re-add event listeners to the new elements
        dropdownToggle.addEventListener('click', function(event) {
            handleDropdownToggle(event); // Use the existing function
        });
    }
});





