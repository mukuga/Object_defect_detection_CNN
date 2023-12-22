// Ini adalah script yang digunakan dalam pembuatan fitur riwayat
// Kode dibawah hanya pajangan saja, untuk penggunaannya kami masukkan kode di bawah langsung ke >> kamera.html

function fetchAndDisplayStatistics() {
  fetch('/get_statistics')
    .then(response => response.json())
    .then(data => {
      displayTable(data, 'upload');
      displayTable(data, 'webcam');
    });
}

function displayTable(data, source) {
  let filteredData = data.filter(item => item.source === source);
  let tableHtml = `<table class='table'><caption>${source.toUpperCase()} Predictions</caption><tr><th>Time</th><th>Image</th><th>Filename</th><th>Prediction</th><th>Action</th></tr>`;

  filteredData.forEach(function (row, index) {
    tableHtml += `<tr><td>${row.time}</td><td><img src="/static/uploads/${row.filename}" alt="Image" width="100"></td><td>${row.filename}</td><td>${row.prediction}</td><td><button onclick="deleteEntry(event, ${index}, '${source}')">Delete</button></td></tr>`;
  });

  tableHtml += "</table>";
  document.getElementById(`hasil-statistik-${source}`).innerHTML = tableHtml;
}


function deleteEntry(event, index, source) {
  event.preventDefault();
  fetch(`/delete_entry/${index}/${source}`, { method: 'DELETE' })
    .then(response => response.json())
    .then(data => {
      if (data.success) {
        fetchAndDisplayStatistics(); // Refresh the list
        // Periksa apakah tabel webcam kosong
        checkIfWebcamTableEmpty();
      } else {
        console.error('Error deleting entry:', data.error);
      }
    })
    .catch(error => console.error('Fetch error:', error));
}


document.addEventListener('DOMContentLoaded', function () {
  fetchAndDisplayStatistics();
});

document.getElementById('delete-all-upload').addEventListener('click', function () {
  deleteAll('upload');
});

document.getElementById('delete-all-webcam').addEventListener('click', function () {
  deleteAll('webcam');
});

function deleteAll(source) {
  if (confirm(`Are you sure you want to delete all ${source} history?`)) {
    fetch(`/delete_all/${source}`, { method: 'DELETE' })
      .then(response => response.json())
      .then(data => {
        if (data.success) {
          fetchAndDisplayStatistics(); // Refresh the list
          if (data.webcam_empty) {
            resetWebcamCount();
          }
        } else {
          console.error(`Error deleting all ${source} entries:`, data.error);
        }
      })
      .catch(error => console.error('Fetch error:', error));
  }
}

function resetWebcamCount() {
  fetch('/reset_count', { method: 'GET' })
    .then(response => response.json())
    .then(data => console.log('Counter reset'))
    .catch(error => console.error('Error resetting counter:', error));
}
