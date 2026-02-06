
function setupUpload() {
  const pick = document.getElementById("pick");
  const fileInput = document.getElementById("fileInput");
  const dz = document.getElementById("dropzone");

  pick.addEventListener("click", () => {
    fileInput.click();
  });

  fileInput.addEventListener("change", async () => {
    const files = Array.from(fileInput.files);
    const form = new FormData();
    for (const f of files) form.append("files", f);
    await fetch("/upload", { method: "POST", body: form });
  });

  dz.addEventListener("dragover", (e) => {
    e.preventDefault(); // muss sein, sonst kein drop [web:479]
  });

  dz.addEventListener("drop", async (e) => {
    e.preventDefault(); // verhindert "Datei öffnen" [web:474]
    const files = Array.from(e.dataTransfer.files);

    const form = new FormData();
    for (const f of files) form.append("files", f);

    const res = await fetch("/upload", { method: "POST", body: form });
    if (!res.ok) console.error(await res.text());
  });
}

setupUpload();

socket.on("ws_ready", (msg) => console.log("ws_ready", msg));
  socket.on("ocr_progress", (msg) => {
    console.log("ocr_progress", msg);
    // hier UI updaten
  });

socket.on("test", msg =>{
    console.log(msg)
})