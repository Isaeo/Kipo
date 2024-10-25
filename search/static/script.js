const fileDrop = document.getElementById("file-drop");
const fileInput = document.getElementById("file-input");
const fileNameInput = document.getElementById("filename");
const substituteButton = document.getElementById("substitute");
const searchQuery = document.getElementById("searchBar");
const loadingDiv = document.getElementById("loading");
const compareButton = document.getElementById("compare");

// Prevent default drag behaviors
['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
  fileDrop.addEventListener(eventName, (e) => {
    e.preventDefault();
    e.stopPropagation();
  }, false);
});

// Add active class when dragging over the file drop area
['dragenter', 'dragover'].forEach(eventName => {
  fileDrop.addEventListener(eventName, () => {
    fileDrop.classList.add("active");
  }, false);
});

// Remove active class when dragging outside the file drop area
['dragleave', 'drop'].forEach(eventName => {
  fileDrop.addEventListener(eventName, () => {
    fileDrop.classList.remove("active");
  }, false);
});

// Handle dropped files
fileDrop.addEventListener('drop', (e) => {
  fileInput.files = e.dataTransfer.files;

  let fileNames_commas = "";
  for (let i = 0; i < fileInput.files.length; i++) {
    fileNames_commas += fileInput.files[i].name + ', ';
  }
  fileNames_commas = fileNames_commas.slice(0, -2)
  fileDrop.querySelector("label").textContent = fileNames_commas;
  fileDrop.querySelector(".file-drop-icon").style.display = "none";
  fileNameInput.value = fileNames_commas;
});

// Handle file selection
fileInput.addEventListener('change', (e) => {
  fileInput.files = e.target.files;
  //Create string from all the filenames
  let fileNames_commas = "";
  for (let i = 0; i < fileInput.files.length; i++) {
    fileNames_commas += fileInput.files[i].name + ', ';
  }
  fileNames_commas = fileNames_commas.slice(0, -2)
  fileDrop.querySelector("label").textContent = fileNames_commas;
  fileDrop.querySelector(".file-drop-icon").style.display = "none";
  fileNameInput.value = fileNames_commas;
});


const animate = () => {
  barWidth++;
  progressBar.style.width = `${barWidth}%`;
};

let barWidth = 0;
loadingDiv.style.display = "none";
substituteButton.addEventListener("click", (e) => {
  loadingDiv.style.display = "block";

  setTimeout(function(){
    loadingDiv.style.display = "none";
  },500);
});
