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

export function documentView(content, title, filename) {
  const popupPreview = document.getElementById("popupPreview");
  const closeBtn = document.getElementById("closePopupPreview");
  const input = document.getElementById("title");
  const preview = document.getElementById("preview");

  input.value = title;

  // render
  marked.setOptions({ breaks: true });
  preview.innerHTML = marked.parse(cleanUpMarkdown(String(content ?? "")));

  // show bootstrap modal
  const modal = bootstrap.Modal.getOrCreateInstance(popupPreview);
  modal.show();

  // your "close" action (optional rename then hide)
  closeBtn.onclick = async () => {
    try {
      await changeDocumentName(title, input.value, filename);
    } finally {
      modal.hide();
    }
  };
}
