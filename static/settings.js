function validatePasswords() {
  const password = document.getElementById("password");
  const confirmPassword = document.getElementById("confirmPassword");
  const passwordMessage = document.getElementById("passwordMessage");

  const a = password.value.trim();
  const b = confirmPassword.value.trim();

  let msg = "";
  if ((a === "" && b !== "") || (a !== "" && b === "")) {
    msg = "Please fill out both password fields.";
  } else if (a !== "" && b !== "" && a !== b) {
    msg = "Passwords do not match.";
  }

  confirmPassword.setCustomValidity(msg);
  passwordMessage.textContent = msg;
}

async function loadPreferedFile() {
  const res = await fetch("/api/prefered_file");
  if (!res.ok) throw new Error(await res.text());
  return await res.json();
}

async function fill_select() {
  const preferedFile = document.getElementById("preferedFile");
  preferedFile.replaceChildren();

  const data = await loadPreferedFile();
  const value = data.prefered_file ?? [];

  for (const item of value) {
    preferedFile.add(new Option(String(item), String(item)));
  }
}

function setupSettings() {
  const settingsEl = document.getElementById("settings");
  const openBtn = document.getElementById("viewSettings");
  const saveSettings = document.getElementById("saveSettings");

  const password = document.getElementById("password");
  const confirmPassword = document.getElementById("confirmPassword");
  const preferedFile = document.getElementById("preferedFile");

  password.addEventListener("input", validatePasswords);
  confirmPassword.addEventListener("input", validatePasswords);

  openBtn.addEventListener("click", async () => {
    const modal = bootstrap.Modal.getOrCreateInstance(settingsEl);
    modal.show();
    await fill_select();
  });

  saveSettings.addEventListener("click", async () => {
    validatePasswords();
    if (!confirmPassword.checkValidity()) return;

    const res = await fetch("/save_settings", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        password: password.value,
        confirm_password: confirmPassword.value,
        prefered_file: preferedFile.value,
      }),
    });

    if (!res.ok) throw new Error(await res.text());

    bootstrap.Modal.getOrCreateInstance(settingsEl).hide();
  });

  // Optional: reset form when closing
  settingsEl.addEventListener("hidden.bs.modal", () => {
    password.value = "";
    confirmPassword.value = "";
    document.getElementById("passwordMessage").textContent = "";
    confirmPassword.setCustomValidity("");
  });
}

setupSettings();
