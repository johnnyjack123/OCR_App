import { createDocumentHistory } from "./dashboard_script.js";


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

socket.on("prefered_file", msg => {
  
})