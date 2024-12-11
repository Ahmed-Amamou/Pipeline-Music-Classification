$(document).ready(function () {
  const uploadArea = $("#upload-area");
  const fileInput = $("#file-input");
  const classifySVM = $("#classify-svm");
  const classifyVGG = $("#classify-vgg");
  const results = $("#results");
  const outputArea = $("#output-area");

  let selectedFile = null;

  // Drag and Drop Handlers
  uploadArea.on("dragover", function (e) {
    e.preventDefault();
    e.stopPropagation();
    uploadArea.addClass("dragging");
  });

  uploadArea.on("dragleave", function (e) {
    e.preventDefault();
    e.stopPropagation();
    uploadArea.removeClass("dragging");
  });

  uploadArea.on("drop", function (e) {
    e.preventDefault();
    e.stopPropagation();
    uploadArea.removeClass("dragging");
    const files = e.originalEvent.dataTransfer.files;
    handleFile(files[0]);
  });

  // File Input Change Handler
  fileInput.on("change", function () {
    const files = fileInput[0].files;
    handleFile(files[0]);
  });

  // Handle File
  function handleFile(file) {
    if (file && file.type === "audio/wav") {
      selectedFile = file;
      uploadArea.find("p").text(`Selected: ${file.name}`);
      classifySVM.prop("disabled", false);
      classifyVGG.prop("disabled", false);
    } else {
      alert("Please upload a valid .wav file.");
      uploadArea.find("p").text("Drag and drop your .wav file here");
    }
  }

  // Simulate Classification API Calls
  function classify(apiEndpoint) {
    if (!selectedFile) {
      alert("No file selected!");
      return;
    }

    const formData = new FormData();
    formData.append("file", selectedFile);

    $.ajax({
      url: apiEndpoint,
      type: "POST",
      data: formData,
      contentType: false,
      processData: false,
      success: function (response) {
        results.text(`Predicted Genre: ${response.prediction}`);
        outputArea.hide().fadeIn(500);
      },
      error: function (xhr) {
        if (xhr.responseJSON && xhr.responseJSON.error) {
          results.text(`Error: ${xhr.responseJSON.error}`);
        } else {
          results.text("An error occurred during classification.");
        }
        outputArea.show();
      },
    });
  }

  // Button Click Handlers
  classifySVM.on("click", function () {
    classify("http://127.0.0.1:5000/predict"); // Replace with your SVM endpoint
  });

  classifyVGG.on("click", function () {
    classify("http://localhost:5000/predict"); // Replace with your VGG endpoint
  });
});
