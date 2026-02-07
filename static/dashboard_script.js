
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

function cleanUpMarkdown(text) {
  // Zeilen, die nur aus "-" (optional mit Spaces) bestehen -> "\-"
  return text.replace(/^\s*-\s*$/gm, "\\-");
}

function documentView(text) {
  const preview = document.getElementById("preview");
  const popupPreview = document.getElementById("popupPreview")
  const closePopupPreview = document.getElementById("closePopupPreview")
  //fileContent.style = "display: block";
  marked.setOptions({ breaks: true });
  const new_text = cleanUpMarkdown(text);
  preview.innerHTML = marked.parse(new_text);
  closePopupPreview.addEventListener("click", () => popupPreview.close());

  popupPreview.showModal();
}

function fillDocumentHistoryList(filename, title) {
  const li = document.createElement("li");

  const btn = document.createElement("button");
  btn.type = "button";
  btn.textContent = title;

  btn.addEventListener("click", () => {
    documentView(content.content)
  });

  li.appendChild(btn);

  const deleteBtn = document.createElement("button");
  const confirmDelete = document.getElementById("confirmDelete");
  const confirmDeleteBtn = document.getElementById("confirmDeleteBtn");
  const abortConfirmDeleteBtn = document.getElementById("abortConfirmDeleteBtn");

  deleteBtn.textContent = "Delete"
  deleteBtn.addEventListener("click", () => {
    confirmDelete.showModal();
  });

  li.appendChild(deleteBtn);

  confirmDeleteBtn.addEventListener("click", async () => {
    const res = await fetch("/delete_document", {
      method: "POST",
      headers: { "Content-Type": "text/plain; charset=utf-8" },
      body: filename,
    });
    if (!res.ok) throw new Error(await res.text());
    confirmDelete.close()
  });

  abortConfirmDeleteBtn.addEventListener("click", () => confirmDelete.close());
  return li;
}

function createDocumentHistory(history) {
  const ul = document.getElementById("documentHistory");
  ul.replaceChildren();

  console.log("History:", history);

  for (const item of history) {
    const [[filename, content]] = Object.entries(item); // erstes (und einziges) Paar [web:438]
    console.log("filename:", filename);
    console.log("content:", content);
    console.log("keys:", content && typeof content === "object" ? Object.keys(content) : typeof content);
    const title = content.title ?? filename;
    console.log("Title: " + title)
    const li = fillDocumentHistoryList(filename, title);

    ul.appendChild(li);
  }
}


//Websockets
const socket = io({ withCredentials: true });

socket.on("connect", () => console.log("socket connected", socket.id));
socket.on("connect_error", (e) => console.error("connect_error", e));

/*socket.on("ws_ready", (msg) => console.log("ws_ready", msg));
  socket.on("ocr_progress", (msg) => {
    console.log("ocr_progress", msg);
    // hier UI updaten
  });*/

socket.on("test", msg => {
  console.log(msg);
})

socket.on("finished_document", msg => {
  console.log(msg);
})

socket.on("document_history", msg => {
  createDocumentHistory(msg);
})