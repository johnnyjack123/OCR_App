
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

async function changeDocumentName(old_title, new_title, filename) {
  if (old_title === new_title || new_title === "") return;
  const res = await fetch("/change_name", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ "filename": filename, "new_title": new_title }),
  });

  if (!res.ok) throw new Error(await res.text());
}

function documentView(content, title, filename) {
  const preview = document.getElementById("preview");
  const popupPreview = document.getElementById("popupPreview");
  const closePopupPreview = document.getElementById("closePopupPreview");
  const input = document.getElementById("title");

  input.value = title

  closePopupPreview.onclick = async () => {
    try {
      await changeDocumentName(title, input.value, filename);
    } catch (e) {
      console.error(e);
    }
    popupPreview.close();
  };

  marked.setOptions({ breaks: true });
  const new_content = cleanUpMarkdown(content);
  preview.innerHTML = marked.parse(new_content);

  popupPreview.showModal();
}

function add_view_button(title, content, filename) {
  const btn = document.createElement("button");
  btn.type = "button";
  btn.textContent = title;

  btn.addEventListener("click", () => {
    documentView(content.content, title, filename)
  });
  return btn;
}

function add_download_button(filename) {
  const downloadBtn = document.createElement("button");
  downloadBtn.textContent = "Download";

  downloadBtn.addEventListener("click", () => {
    // filename sicher encoden, dann GET-Download starten
    const url = `/download/${encodeURIComponent(filename)}`;
    window.location.href = url; // triggert Download ganz normal
  });

  return downloadBtn;
}

function add_delete_button() {
  const deleteBtn = document.createElement("button");
  deleteBtn.textContent = "Delete"
  deleteBtn.addEventListener("click", () => {
    confirmDelete.showModal();
  });
  return deleteBtn;
}

function fill_delete_modal(filename) {
  const confirmDelete = document.getElementById("confirmDelete");
  const confirmDeleteBtn = document.getElementById("confirmDeleteBtn");
  const abortConfirmDeleteBtn = document.getElementById("abortConfirmDeleteBtn");

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
}

function fillDocumentHistoryList(filename, content, title) {
  const li = document.createElement("li");

  const view_btn = add_view_button(title, content, filename);

  li.appendChild(view_btn);

  const downloadBtn = add_download_button(filename)

  li.appendChild(downloadBtn)

  const deleteBtn = add_delete_button();

  li.appendChild(deleteBtn);

  fill_delete_modal(filename)

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
    const li = fillDocumentHistoryList(filename, content, title);

    ul.appendChild(li);
  }
}

function validateMatch() {
  const password = document.getElementById("password");
  const confirmPassword = document.getElementById("confirmPassword");
  const passwordMessage = document.getElementById("passwordMessage");

  const a = password.value;
  const b = confirmPassword.value;

  if (a && b && a !== b) {
    confirmPassword.setCustomValidity("Passwörter stimmen nicht überein."); // macht Feld invalid [web:108]
    passwordMessage.textContent = "Passwörter stimmen nicht überein.";
  } else {
    confirmPassword.setCustomValidity(""); // Fehler zurücksetzen [web:108]
    passwordMessage.textContent = "";
  }
}

function validateBothOrNone() {
  const password = document.getElementById("password");
  const confirmPassword = document.getElementById("confirmPassword");
  const passwordMessage = document.getElementById("passwordMessage");

  const a = password.value.trim();
  const b = confirmPassword.value.trim();

  // entweder beide leer ODER beide gefüllt
  const ok = (a === "" && b === "") || (a !== "" && b !== "");

  if (!ok) {
    // du kannst die Meldung auf einem der beiden Felder setzen (oder auf beiden)
    confirmPassword.setCustomValidity("Bitte beide Felder ausfüllen.");
    passwordMessage.textContent = "Bitte beide Felder ausfüllen.";
  } else {
    confirmPassword.setCustomValidity("");
    passwordMessage.textContent = "";
  }
}

function setupSettings() {
  const password = document.getElementById("password");
  const confirmPassword = document.getElementById("confirmPassword");
  const preferedFile = document.getElementById("preferedFile");
  const saveSettings = document.getElementById("saveSettings");
  const closeSettings = document.getElementById("closeSettings")

  saveSettings.addEventListener("click", async () => {
    const res = await fetch("/save_settings", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ "password": password, "confirm_password": confirmPassword, "prefered_file": preferedFile }),
    });
    if (!res.ok) throw new Error(await res.text());
  });

  password.addEventListener("input", () => { validateBothOrNone(); validateMatch(); });
  confirmPassword.addEventListener("input", () => { validateBothOrNone(); validateMatch(); });
  closeSettings.addEventListener("click", () => {
    settings.close();
  });
}

setupSettings();

function viewSettings(){
  viewSettings = document.getElementById("viewSettings");
  viewSettings.addEventListener("click", () => {
    settings.showModal();
  });
}

viewSettings();

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