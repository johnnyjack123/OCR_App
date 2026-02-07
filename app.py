import utils.global_variables as global_variables
from pathlib import Path

UPLOAD_DIR = Path("./uploads")
TEXT_FILE_DIR = Path("./results")
global_variables.result_folder_path = TEXT_FILE_DIR
global_variables.upload_folder_path = UPLOAD_DIR

PROJECT_DIR = Path(__file__).resolve().parent
global_variables.project_dir = PROJECT_DIR

from flask import Flask, request, redirect, url_for, render_template, send_file, abort
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from flask_socketio import SocketIO, emit
from werkzeug.security import check_password_hash
from werkzeug.utils import secure_filename
from utils.file_handler import load_and_migrate, UserStore, load_file, read_result, delete_result_file, save_file, edit_result
from utils.check_env_variables import check_env_variables
from sockets.app_factory import create_app
from sockets.extensions import socketio
import argparse
from io import BytesIO
from admin import add_user_dialog
from utils.logger import logger
from ocr_worker import add_ocr_task, start_worker
from sockets.sockets import socketio_push, send_document_history

# Creates necessary folders to execute script
def create_folders():
    UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
    TEXT_FILE_DIR.mkdir(parents=True, exist_ok=True)

store = UserStore("./userdata.json")  # aus deinem Code

app = create_app()

#app.config["SECRET_KEY"] = "BITTE_HIER_EINEN_LANGEN_RANDOM_SECRET_SETZEN"  # nötig für Sessions [web:80]
#socketio = SocketIO(app, async_mode="threading", cors_allowed_origins="*")  # für Tests ok

login_manager = LoginManager(app)
login_manager.login_view = "login"

class WebUser(UserMixin):
    def __init__(self, username: str):
        self.id = username  # Flask-Login nutzt .get_id() → default ist str(self.id)

@login_manager.user_loader
def load_user(user_id: str):
    u = store.get_user(user_id)  # username als ID
    if u is None:
        return None  # Flask-Login will None statt Exception [web:71]
    return WebUser(u.username)

@app.route("/", methods=["GET", "POST"])
def index():
    return redirect(url_for("login"))

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "GET":
        return render_template("login.html")

    username = request.form.get("username", "")
    password = request.form.get("password", "")
    u = store.get_user(username)
    if not u:
        return "Invalid credentials", 401

    # Variante A: wenn du werkzeug generate_password_hash benutzt hast:
    if not check_password_hash(u.password_hash, password):
        return "Invalid credentials", 401  # check_password_hash vergleicht Plaintext mit Hash [web:81]
    logger.info(f"Login from user: {username}")
    login_user(WebUser(u.username))
    return redirect(url_for("dashboard"))

@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("login"))

@app.route("/dashboard", methods=["GET"])
@login_required
def dashboard():
    exists = False
    username = current_user.get_id()
    userdata = load_file()
    file_access = None
    for user in userdata.users:
        if user.username == username:
            exists = True
            print("User found.")
            file_access = user.text_files
            break

    if not exists:
        logger.error("Username not found.")
        return render_template("dashboard.html")
    
    file_content = []

    if file_access:
        for file in file_access:
            file_content.append(read_result(file))
    socketio_push("test", "test", username)
    return render_template("dashboard.html", file_content=file_content)

@app.route("/add_task", methods=["POST"])
@login_required
def add_task():
    request.form.get("")
    return redirect(url_for("dashboard"))

@app.route("/delete_document", methods=["POST"])
@login_required
def delete_document():
    username = current_user.get_id()
    file_name = request.get_data(as_text=True).strip()
    print(f"Filename: {file_name}")
    file = load_file()
    for user in file.users:
        if user.username == username:
            print("User found.")
            if file_name in user.text_files:
               user.text_files.remove(file_name)
               print("Remove file from json.")
               save_file(file)
               break
    delete_result_file(file_name)
    send_document_history(username)
    return redirect(url_for("dashboard"))

@app.route("/upload", methods=["POST"])
@login_required
def upload():
    username = current_user.get_id()

    files = request.files.getlist("files")
    if not files:
        return "No files", 400

    for file in files:
        filename = secure_filename(file.filename)  # niemals ungeprüfte Dateinamen nutzen [web:157]
        save_path = UPLOAD_DIR / filename
        file.save(save_path)  # speichert auf disk [web:157]
        print("Received Image.")
        add_ocr_task(username, filename)
    return redirect(url_for("dashboard"))

@app.route("/download/<path:filename>")
@login_required
def download(filename):
    result_file = read_result(filename)
    
    buf = BytesIO(result_file["content"].encode("utf-8"))
    buf.seek(0)  # wichtig, damit ab Anfang gelesen wird [web:38]

    title = result_file["title"]

    try:
        return send_file(
                buf,
                as_attachment=True,                 # Browser soll downloaden [web:38]
                download_name=f"{title}.txt",         # Dateiname beim Client (Flask >= 2.0)
                mimetype="text/plain; charset=utf-8"
        )
    except FileNotFoundError:
        abort(404)

@app.route("/change_name", methods=["POST"])
@login_required
def change_name():
    logger.info("Change name.")
    username = current_user.get_id()
    data = request.get_json(silent=True) or {}
    filename = data["filename"]
    new_title = data["new_title"]
    result_file = read_result(filename)
    result_file["title"] = new_title
    edit_result(filename, result_file)
    send_document_history(username)
    return redirect(url_for("dashboard"))

def parse_arguments():
    parser = argparse.ArgumentParser()
    parser.add_argument("--add_user", action="store_true",
                        help="Add user")
    parser.add_argument("--check_env_variables", action="store_true",
                        help="Add user")
    args = parser.parse_args()

    if args.add_user:
        add_user_dialog()
        return
    
    if args.check_env_variables:
        check_env_variables()
        return

if __name__ == '__main__':
    create_folders()
    parse_arguments()
    load_and_migrate()
    start_worker()
    file = load_file()
    debug_mode = file.debug_mode
    socketio.run(app, host="0.0.0.0", port=5000, debug=debug_mode)



# TODO: machen, dass wenn Datei nicht gefunden wird, nicht gesamter Server hängt, sondern nur in Browser angezeigt wird
# TODO: Dateinamen ändern
# TODO: bevorzugter Dateidownload von txt oder md Datein