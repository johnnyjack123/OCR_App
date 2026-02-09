import { documentView } from "./document_view.js";

function add_view_button(title, content, filename) {
  const btn = document.createElement("button");
  btn.type = "button";
  if (title == false) {
    btn.textContent = "Missing document"
  } else {
    btn.textContent = "View";

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

function openDeleteModal(filename) {
  pendingDeleteFilename = filename;
  const el = document.getElementById("confirmDelete");
  const modal = bootstrap.Modal.getOrCreateInstance(el);
  modal.show();
}

function setupDeleteModal() {
  const el = document.getElementById("confirmDelete");
  const confirmDeleteBtn = document.getElementById("confirmDeleteBtn");

  confirmDeleteBtn.onclick = async () => {
    if (!pendingDeleteFilename) return;

    const filename = pendingDeleteFilename;
    pendingDeleteFilename = null;

    try {
      const res = await fetch("/delete_document", {
        method: "POST",
        headers: { "Content-Type": "text/plain; charset=utf-8" },
        body: filename,
      });
      if (!res.ok) throw new Error(await res.text());

      bootstrap.Modal.getOrCreateInstance(el).hide();
    } catch (e) {
      console.error(e);
      // Optional: show an alert area in modal
    }
  };

  // When modal closes, clear pending (safety)
  el.addEventListener("hidden.bs.modal", () => {
    pendingDeleteFilename = null;
  });
}

function add_delete_button(filename) {
  const deleteBtn = document.createElement("button");
  deleteBtn.textContent = "Delete";
  deleteBtn.type = "button";
  deleteBtn.classList.add("btn", "btn-outline-danger", "btn-sm");

  deleteBtn.addEventListener("click", () => openDeleteModal(filename));
  return deleteBtn;
}

setupDeleteModal();

function fillDocumentHistoryList(filename, content, title) {
  const li = document.createElement("li");

  const card = document.createElement("div");
  card.className = "card shadow-sm h-100 overflow-hidden position-relative";

  const cardBody = document.createElement("div");
  cardBody.className = "card-body";

  const headerRow = document.createElement("div");
  headerRow.className = "d-flex align-items-start justify-content-between gap-2";

  const titleWrap = document.createElement("div");
  titleWrap.className = "min-w-0";

  const h = document.createElement("div");
  h.className = "fw-semibold truncate-1";
  h.title = title === false ? "Missing document" : title;
  h.textContent = title === false ? "Missing document" : title;

  const meta = document.createElement("div");
  meta.className = "text-secondary small truncate-1";
  meta.title = filename;
  meta.textContent = filename;

  titleWrap.appendChild(h);
  titleWrap.appendChild(meta);

  // Decide badge state (better than title===false)
  const isReady = Boolean(content?.content);

  const badge = document.createElement("span");
  badge.className = (isReady ? "badge text-bg-success" : "badge text-bg-warning") + " corner-badge";
  badge.textContent = isReady ? "Ready" : "Missing";

  headerRow.appendChild(titleWrap);
  headerRow.appendChild(badge);

  const btnRow = document.createElement("div");
  btnRow.className = "d-flex flex-wrap gap-2 mt-3";

  const viewBtn = add_view_button(title, content, filename);
  viewBtn.classList.add("btn", "btn-outline-secondary", "btn-sm");
  btnRow.appendChild(viewBtn);

  if (isReady) {
    const downloadBtn = add_download_button(filename);
    downloadBtn.classList.add("btn", "btn-primary", "btn-sm");
    btnRow.appendChild(downloadBtn);
  }

  const deleteBtn = add_delete_button(filename);
  btnRow.appendChild(deleteBtn);

  cardBody.appendChild(headerRow);
  cardBody.appendChild(btnRow);
  card.appendChild(cardBody);
  li.appendChild(card);

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