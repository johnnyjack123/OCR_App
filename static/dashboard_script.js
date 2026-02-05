
function addEventListeners() {
    document.getElementById("pick").addEventListener("click", () => {
        document.getElementById("fileInput").click();

        const dz = document.getElementById("dropzone");

        dz.addEventListener("dragover", (e) => e.preventDefault());
        dz.addEventListener("drop", async (e) => {
            e.preventDefault();

            // Einfachster Fall: Files-Liste (funktioniert für normale Files)
            const files = Array.from(e.dataTransfer.files);

            const form = new FormData();
            for (const f of files) form.append("files", f);

            await fetch("/upload", { method: "POST", body: form });
        });

    });
}

addEventListeners();