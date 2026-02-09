function setupUpload() {
  const pick = document.getElementById("pick");
  const fileInput = document.getElementById("fileInput");
  const dz = document.getElementById("dropzone");

  pick.addEventListener("click", () => fileInput.click());

  fileInput.addEventListener("change", async () => {
    const files = Array.from(fileInput.files);
    if (files.length === 0) return;

    const form = new FormData();
    for (const f of files) form.append("files", f);

    try {
      const res = await fetch("/upload", { method: "POST", body: form });
      if (!res.ok) console.error(await res.text());
    } finally {
      fileInput.value = ""; // wichtig: erlaubt gleiche Datei erneut auszuwählen [web:356]
    }
  });

  dz.addEventListener("dragover", (e) => e.preventDefault());

  dz.addEventListener("drop", async (e) => {
    e.preventDefault();
    const files = Array.from(e.dataTransfer.files);
    if (files.length === 0) return;

    const form = new FormData();
    for (const f of files) form.append("files", f);

    const res = await fetch("/upload", { method: "POST", body: form });
    if (!res.ok) console.error(await res.text());
  });
}

setupUpload();
