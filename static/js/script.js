// static/js/script.js
// This file can be empty initially, just create it

document.addEventListener('DOMContentLoaded', function() {
    // Add your JavaScript code here
    
    // Example: Make tables responsive
    const tables = document.querySelectorAll('table');
    tables.forEach(table => {
        table.classList.add('table-responsive');
    });
    
    // Example: Initialize tooltips
    var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    var tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });
});