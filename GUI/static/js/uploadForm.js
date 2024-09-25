var inputFiles = document.getElementById("files");
function createAlert(message, status) {
  const alert = document.getElementById("alert-mess");
  alert.style.display = "block";
  let alertClass = (color) =>
    `bg-${color}-100 border-${color}-400 text-${color}-700`.split(" ");
  alert.classList.add(...alertClass(status === "error" ? "red" : "green"));
  alert.classList.remove(...alertClass(status === "error" ? "green" : "red"));
  alert
    .querySelector("svg")
    .classList.add(`text-${status === "error" ? "red" : "green"}-500`);
  alert
    .querySelector("svg")
    .classList.remove(`text-${status === "error" ? "green" : "red"}-500`);

  alert.querySelector("strong").textContent =
    status === "error" ? "Error!" : "Success!";

  alert.querySelector("#alert-mess-text").textContent = message;
}
function humanFileSize(size) {
  const i = Math.floor(Math.log(size) / Math.log(1024));
  return (
    (size / Math.pow(1024, i)).toFixed(2) * 1 +
    " " +
    ["B", "kB", "MB", "GB", "TB"][i]
  );
}
function dataFileDnD() {
  return {
    files: [],
    fileDragging: null,
    fileDropping: null,
    humanFileSize(size) {
      const i = Math.floor(Math.log(size) / Math.log(1024));
      return (
        (size / Math.pow(1024, i)).toFixed(2) * 1 +
        " " +
        ["B", "kB", "MB", "GB", "TB"][i]
      );
    },
    type(file) {
      const type = file.type.split("/")[0];
      return type;
    },
    remove(index) {
      let files = [...this.files];
      files.splice(index, 1); // remove the file

      this.files = createFileList(files);
      inputFiles.files = this.files;
    },
    drop(e) {
      let removed, add;
      let files = [...this.files];

      removed = files.splice(this.fileDragging, 1);
      files.splice(this.fileDropping, 0, ...removed);

      this.files = createFileList(files);

      this.fileDropping = null;
      this.fileDragging = null;
      inputFiles.files = this.files;
    },
    dragenter(e) {
      let targetElem = e.target.closest("[draggable]");

      this.fileDropping = targetElem.getAttribute("data-index");
    },
    dragstart(e) {
      this.fileDragging = e.target
        .closest("[draggable]")
        .getAttribute("data-index");
      e.dataTransfer.effectAllowed = "move";
    },
    loadFile(file) {
      const preview = document.querySelectorAll(".preview");
      const blobUrl = URL.createObjectURL(file);

      preview.forEach((elem) => {
        elem.onload = () => {
          URL.revokeObjectURL(elem.src); // free memory
        };
      });
      return blobUrl;
    },
    addFiles(e) {
      const files = createFileList([...this.files], [...e.target.files]);
      this.files = files;
      inputFiles.files = this.files;
    },
  };
}

function hideAlert() {
  timeout = setTimeout(() => {
    document.querySelector("#alert-mess").style.display = "none";
    document.getElementById("outputs").parentElement.classList.add("mt-15");
  }, 5000);
}

function submitForm(e) {
  e.preventDefault();
  const allFiles = inputFiles.files;
  if (allFiles.length === 0) {
    createAlert("Please select a file to process.", "error");
    hideAlert();
    return;
  }
  // if total file size is greater than 100MB
  const totalSize = Array.from(allFiles).reduce(
    (acc, file) => acc + file.size,
    0
  );
  if (totalSize >= 100 * 1024 * 1024) {
    createAlert(
      `Total file size (${humanFileSize(
        totalSize
      )}) exceeds 100MB. Please try again!`,
      "error"
    );
    hideAlert();
    return;
  }
  const form = document.getElementById("uploadForm");
  const formData = new FormData(form);
  form.submit();
}
