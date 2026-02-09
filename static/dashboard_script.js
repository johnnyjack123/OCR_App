import { documentView } from "./document_view.js";

function add_view_button(title, content, filename) {
  const btn = document.createElement("button");
  btn.type = "button";
  if (title == false) {
    btn.textContent = "Missing document"
  } else {
    btn.textContent = title;

    btn.addEventListener("click", () => {
      documentView(content.content, title, filename)
    });
  }
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

let pendingDeleteFilename = null;

function setupDeleteModal() {
  const confirmDelete = document.getElementById("confirmDelete");
  const confirmDeleteBtn = document.getElementById("confirmDeleteBtn");
  const abortConfirmDeleteBtn = document.getElementById("abortConfirmDeleteBtn");

  confirmDeleteBtn.onclick = async () => {
    if (!pendingDeleteFilename) return;

    const filename = pendingDeleteFilename;
    pendingDeleteFilename = null;

    const res = await fetch("/delete_document", {
      method: "POST",
      headers: { "Content-Type": "text/plain; charset=utf-8" },
      body: filename,
    });

    if (!res.ok) throw new Error(await res.text());
    confirmDelete.close();
  };

  abortConfirmDeleteBtn.onclick = () => {
    pendingDeleteFilename = null;
    confirmDelete.close();
  };
}

function add_delete_button(filename) {
  const deleteBtn = document.createElement("button");
  deleteBtn.textContent = "Delete";
  deleteBtn.type = "button";

  deleteBtn.addEventListener("click", () => {
    pendingDeleteFilename = filename;
    document.getElementById("confirmDelete").showModal();
  });

  return deleteBtn;
}

setupDeleteModal();


function fillDocumentHistoryList(filename, content, title) {

  const li = document.createElement("li");
  const downloadBtn = add_download_button(filename)

  const view_btn = add_view_button(title, content, filename);

  li.appendChild(view_btn);

  if (title != false) {
    li.appendChild(downloadBtn)
  }
  const deleteBtn = add_delete_button(filename);
  li.appendChild(deleteBtn);
  return li;
}

export function createDocumentHistory(history) { // export to access function from other files
  const ul = document.getElementById("documentHistory");
  ul.replaceChildren();

  for (const item of history) {
    const [[filename, content]] = Object.entries(item);
    const title = content.title ?? filename;
    const li = fillDocumentHistoryList(filename, content, title);
    ul.appendChild(li);
  }
}


export function updateProgress(msg) {
  const progress = document.getElementById("progress");
  progress.innerHTML = msg;
}