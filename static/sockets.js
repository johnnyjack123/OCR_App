import { createDocumentHistory } from "./dashboard_script.js";
import { updateProgress } from "./dashboard_script.js";


const socket = io({ withCredentials: true });

socket.on("connect", () => console.log("socket connected", socket.id));
socket.on("connect_error", (e) => console.error("connect_error", e));

/*socket.on("finished_document", msg => {
  console.log(msg);
})*/

socket.on("document_history", msg => {
  createDocumentHistory(msg);
})

socket.on("progress", msg => {
  updateProgress(msg);
})