function validatePasswords() {
  const password = document.getElementById("password");
  const confirmPassword = document.getElementById("confirmPassword");
  const passwordMessage = document.getElementById("passwordMessage");

  const a = password.value.trim();
  const b = confirmPassword.value.trim();

  let msg = "";

  // Regel 1: Wenn eins gefüllt ist, muss das andere auch gefüllt sein
  if ((a === "" && b !== "") || (a !== "" && b === "")) {
    msg = "Bitte beide Felder ausfüllen.";
  }
  // Regel 2: Wenn beide gefüllt sind, müssen sie gleich sein
  else if (a !== "" && b !== "" && a !== b) {
    msg = "Passwörter stimmen nicht überein.";
  }

  confirmPassword.setCustomValidity(msg);   // non-empty => invalid, empty => valid [web:108][web:128]
  passwordMessage.textContent = msg;
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
      body: JSON.stringify({ "password": password.value, "confirm_password": confirmPassword.value, "prefered_file": preferedFile.value }),
    });
    if (!res.ok) throw new Error(await res.text());
  });

  password.addEventListener("input", () => { validatePasswords(); });
  confirmPassword.addEventListener("input", () => { validatePasswords(); });
  closeSettings.addEventListener("click", () => {
    settings.close();
  });
}

setupSettings();

function viewSettings() {
  viewSettings = document.getElementById("viewSettings");
  viewSettings.addEventListener("click", async () => {
    settings.showModal();
    await fill_select();
  });
}

viewSettings();

async function loadHistory() {
  const res = await fetch("/api/prefered_file");   // GET ist Default [web:64]
  if (!res.ok) throw new Error(await res.text());
  const data = await res.json();             // JSON -> JS-Objekt/Array [web:64]
  return data;
}

async function fill_select() {
  const preferedFile = document.getElementById("preferedFile");
  preferedFile.replaceChildren();

  const data = await loadHistory();   // WICHTIG: await [web:94]
  const value = data.prefered_file;   // das ist dein Array

  for (const item of value) {
    // falls item bool sein kann, als Text darstellen
    preferedFile.add(new Option(String(item), String(item)));
  }
}
