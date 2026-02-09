function uploadFiles(files) {
  const list = Array.from(files ?? []);
  if (list.length === 0) return;

  const form = new FormData();
  for (const f of list) form.append("files", f);

  return fetch("/upload", { method: "POST", body: form })
    .then(async (res) => {
      if (!res.ok) throw new Error(await res.text());
    })
    .catch((e) => console.error(e));
}

function setupUpload() {
  const pick = document.getElementById("pick");
  const fileInput = document.getElementById("fileInput");
  const dz = document.getElementById("dropzone");

  pick.addEventListener("click", () => fileInput.click());

  fileInput.addEventListener("change", async () => {
    try {
      await uploadFiles(fileInput.files);
    } finally {
      fileInput.value = "";
    }
  });

  // Prevent browser from opening the file when dropped outside the dropzone
  document.addEventListener("dragover", (e) => {
    e.preventDefault();
  });

  document.addEventListener("drop", async (e) => {
    e.preventDefault();
    await uploadFiles(e.dataTransfer?.files);
    dz.classList.remove("dragover");
  });

  // Visual highlight only when dragging files
  document.addEventListener("dragenter", (e) => {
    if (e.dataTransfer?.types?.includes("Files")) dz.classList.add("dragover");
  });

  document.addEventListener("dragleave", (e) => {
    // Only remove highlight when leaving the window/document
    if (e.relatedTarget === null) dz.classList.remove("dragover");
  });

  // Keep your existing dropzone behavior too (optional)
  dz.addEventListener("dragover", (e) => e.preventDefault());
  dz.addEventListener("drop", async (e) => {
    e.preventDefault();
    await uploadFiles(e.dataTransfer?.files);
    dz.classList.remove("dragover");
  });
}

setupUpload();
