// Function to display flash messages
function displayFlashMessage(message, status) {
  const flashMessageDiv = document.getElementById("flash-message");
  flashMessageDiv.classList.remove("hidden");
  flashMessageDiv.innerText = message;

  // Styling based on status
  if (status === "success") {
    flashMessageDiv.classList.add("bg-green-100", "text-green-700");
    flashMessageDiv.classList.remove("bg-red-100", "text-red-700");
  } else if (status === "error") {
    flashMessageDiv.classList.add("bg-red-100", "text-red-700");
    flashMessageDiv.classList.remove("bg-green-100", "text-green-700");
  }
}

// main functionality
const socket = io.connect("http://" + document.domain + ":" + location.port);
let fileId = undefined;

function uploadFile() {
  const flashMessageDiv = document.getElementById("flash-message");

  const fileInput = document.getElementById("fileInput");
  const file = fileInput.files[0];
  const chunkSize = 64 * 1024; // 64 KB per chunk, adjust as needed
  const reader = new FileReader();
  let currentChunk = 0;

  if (!file && !flashMessageDiv.classList.contains("hidden")) {
    const flashMessageDiv = document.getElementById("flash-message");
    flashMessageDiv.classList.add("hidden");
    document.getElementById("feature-selection").classList.add("hidden");
  }

  // Helper function to send chunks
  function sendChunk() {
    const start = currentChunk * chunkSize;
    const end = Math.min(start + chunkSize, file.size);
    const blob = file.slice(start, end);

    reader.readAsArrayBuffer(blob);
  }

  reader.onload = function (event) {
    const fileData = event.target.result;
    const isLastChunk = currentChunk * chunkSize + chunkSize >= file.size;
    fileId = file.name;

    // Emit each chunk with an identifier to reconstruct on the server
    socket.emit("upload_file_chunk", {
      fileId: file.name, // Or use a unique ID per upload session
      chunk: fileData,
      isLastChunk: isLastChunk,
      extension: file.type.split("/")[1],
    });

    // Process the next chunk
    currentChunk++;
    if (!isLastChunk) {
      sendChunk();
    }
  };

  // Start sending chunks
  if (file) sendChunk();
}

function onFeatureSelectionChange(e) {
  // Gather independent and dependent features
  const independentFeatures = Array.from(
    document.querySelectorAll('input[name="independent"]:checked')
  ).map((input) => input.value);
  const dependentFeature = document.querySelector(
    'input[name="dependent"]:checked'
  )
    ? document.querySelector('input[name="dependent"]:checked').value
    : null;

  // Emit selected features to the server
  if (dependentFeature) {
    socket.emit("set_features", {
      independent: independentFeatures,
      dependent: dependentFeature,
      fileId
    });
  }
}

// Listen for the 'dataset' event and populate the table
socket.on("upload_complete", (response) => {

  displayFlashMessage(response.message, response.status);
  if (response.keys) {
    const features = response.keys;
    // Show the feature selection section
    document.getElementById("feature-selection").classList.remove("hidden");

    // Populate dependent features radio buttons
    const dependentContainer = document.getElementById("dependent-features");
    dependentContainer.innerHTML = features
      .map(
        (feature) => `
      <label class="block">
        <input type="radio" name="dependent" value="${feature}" class="mr-2" onchange="onFeatureSelectionChange()">
        ${feature}
      </label>
    `
      )
      .join("");

    // Populate independent features checkboxes
    const independentContainer = document.getElementById(
      "independent-features"
    );
    independentContainer.innerHTML = features
      .map(
        (feature) => `
      <label class="block">
        <input type="checkbox" name="independent" value="${feature}" class="mr-2" onchange="onFeatureSelectionChange()">
        ${feature}
      </label>
    `
      )
      .join("");
  }
});

socket.on("plot_image", (data) => {
  const imgElement = document.getElementById("plot-image");
  imgElement.classList.remove('hidden')
  imgElement.src = data.image;
});