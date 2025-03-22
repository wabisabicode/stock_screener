const socket = io();

socket.on('new_result', function(data) {
    const resultsContainer = document.getElementById('results-container');
    const newRow = document.createElement('tr');
    newRow.innerHTML = `<td>${data.stock}</td><td>${data.data}</td>`;
    resultsContainer.appendChild(newRow);
});