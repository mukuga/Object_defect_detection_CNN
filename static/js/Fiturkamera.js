// Ini adalah script yang digunakan dalam pembuatan fitur kamera
// Kode dibawah hanya pajangan saja, untuk penggunaannya kami masukkan kode di bawah langsung ke >> kamera.html


let video = document.getElementById("videoElement");
let canvas = document.getElementById("canvas");
let context = canvas.getContext('2d');
let isStreaming = false;
let imageCaptured = false;
let imageDataUrl = '';

if (navigator.mediaDevices.getUserMedia) {
  navigator.mediaDevices.getUserMedia({ video: { width: 300, height: 300 } })
    .then(function (stream) {
      video.srcObject = stream;
      video.width = 300; // Set video element width
      video.height = 300; // Set video element height
    })
    .catch(function (error) {
      console.log("Something went wrong with the webcam!");
    });
}

document.getElementById('mulai-kamera').addEventListener('click', function () {
  video.style.display = 'block'; // Show the video element
  canvas.style.display = 'none'; // Hide the canvas
  video.play();
  isStreaming = true;
});

document.getElementById('ambil-gambar').addEventListener('click', function () {
  if (isStreaming) {
    context.drawImage(video, 0, 0, 300, 300);
    imageDataUrl = canvas.toDataURL('image/jpeg');
    imageCaptured = true;
    video.style.display = 'none'; // Hide the video element
    canvas.style.display = 'block'; // Show the canvas

    var flash = document.createElement('div');
    flash.className = 'flash';
    document.body.appendChild(flash);
    setTimeout(function () {
      flash.style.opacity = 1;
    }, 100);
    setTimeout(function () {
      flash.style.opacity = 0;
      document.body.removeChild(flash);
    }, 500); // Flash akan hilang setelah 0.5 detik

    fetch('/get_current_count')
      .then(response => response.json())
      .then(data => {
        let currentCount = data.count;
        document.getElementById('image-name').textContent = `image_${currentCount + 0}`;
      });
  }
});

document.getElementById('mulai-prediksi').addEventListener('click', function () {
  if (imageCaptured) {
    fetch('/webcam_predict', {
      method: 'POST',
      body: JSON.stringify({ image: imageDataUrl }),
      headers: {
        'Content-Type': 'application/json'
      }
    })
      .then(response => response.json())
      .then(data => {
        document.getElementById('hasil-prediksi').textContent =
          `Filename: ${data.filename}, Prediction: ${data.prediction}`;
      });

    // After taking a picture and getting a prediction
    fetch('/get_current_count')
      .then(response => response.json())
      .then(data => {
        let count = data.count;
        // Display the image name like 'image_1', 'image_2' etc.
      });

  }
});