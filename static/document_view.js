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