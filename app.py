import global_variables
from pathlib import Path

UPLOAD_DIR = Path("./uploads")
TEXT_FILE_DIR = Path("./results")
global_variables.result_folder_path = TEXT_FILE_DIR

PROJECT_DIR = Path(__file__).resolve().parent
global_variables.project_dir = PROJECT_DIR

from flask import Flask, request, redirect, url_for, render_template
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from werkzeug.security import check_password_hash
from werkzeug.utils import secure_filename
from file_handler import load_and_migrate, UserStore, load_file, read_result
import argparse
from admin import add_user_dialog
from logger import logger
from ocr_worker import add_ocr_task

# Creates necessary folders to execute script
def create_folders():
    UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
    TEXT_FILE_DIR.mkdir(parents=True, exist_ok=True)

store = UserStore("./userdata.json")  # aus deinem Code

app = Flask(__name__)
app.config["SECRET_KEY"] = "BITTE_HIER_EINEN_LANGEN_RANDOM_SECRET_SETZEN"  # nötig für Sessions [web:80]

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
    username = current_user.get_id()
    userdata = load_file()
    file_access = None
    for user in userdata.users:
        if user.username == username:
            file_access = user.text_files
            break

    if not file_access:
        logger.error("Username not found.")
        return render_template("dashboard.html")
    
    file_content = []

    for file in file_access:
        file_content.append(read_result(file))

    return render_template("dashboard.html", file_content=file_content)

@app.route("/add_task", methods=["POST"])
@login_required
def add_task():
    request.form.get("")
    return redirect(url_for("dashboard"))

@app.route("/protected")
@login_required
def protected():
    return f"Hi {current_user.get_id()}, du bist eingeloggt."

@app.route("/upload", methods=["POST"])
@login_required
def upload():
    username = current_user.get_id()

    files = request.files.getlist("files")
    if not files:
        return "No files", 400

    for file in files:
        filename = secure_filename(file)  # niemals ungeprüfte Dateinamen nutzen [web:157]
        save_path = UPLOAD_DIR / filename
        file.save(save_path)  # speichert auf disk [web:157]
        add_ocr_task(username, filename)
    return redirect(url_for("dashboard"))

def parse_arguments():
    parser = argparse.ArgumentParser()
    parser.add_argument("--add_user", action="store_true",
                        help="Add user")
    args = parser.parse_args()

    if args.add_user:
        add_user_dialog()
        return

if __name__ == '__main__':
    create_folders()
    parse_arguments()
    load_and_migrate()
    app.run(host="0.0.0.0", port=5000, debug=True)



