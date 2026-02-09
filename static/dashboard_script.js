import { documentView } from "./document_view.js";

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

export function createDocumentHistory(history) { // export to access function from other files
  const ul = document.getElementById("documentHistory");
  ul.replaceChildren();

  console.log("History:", history);

  for (const item of history) {
    const [[filename, content]] = Object.entries(item); 
    console.log("filename:", filename);
    console.log("content:", content);
    console.log("keys:", content && typeof content === "object" ? Object.keys(content) : typeof content);
    const title = content.title ?? filename;
    console.log("Title: " + title)
    const li = fillDocumentHistoryList(filename, content, title);

    ul.appendChild(li);
  }
}
