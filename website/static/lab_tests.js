document.addEventListener("DOMContentLoaded", function() {
const table = document.getElementById("lab-tests-table");
const prevBtn = document.querySelector(".prev-btn");
const nextBtn = document.querySelector(".next-btn");
const headers = document.querySelectorAll("th");
const cells = document.querySelectorAll("tbody tr td");
let startIndex = 0;
const visibleColumns = 6;

updateColumnsVisibility();

prevBtn.addEventListener("click", function() {
  startIndex = Math.max(0, startIndex - visibleColumns);
  updateColumnsVisibility();
});

nextBtn.addEventListener("click", function() {
  startIndex = Math.min(headers.length - visibleColumns, startIndex + visibleColumns);
  updateColumnsVisibility();
});

function updateColumnsVisibility() {
  headers.forEach((header, index) => {
    if (index === 0 || (index >= startIndex && index < startIndex + visibleColumns)) {
      header.style.display = "table-cell";
    } else {
      header.style.display = "none";
    }
  });

  cells.forEach((cell, index) => {
    const columnIndex = index % headers.length;
    const rowIndex = Math.floor(index / headers.length);
    if (columnIndex === 0 || (columnIndex >= startIndex && columnIndex < startIndex + visibleColumns)) {
      cell.style.display = "table-cell";
    } else {
      cell.style.display = "none";
    }
  });
}
});