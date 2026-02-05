from flask import Flask, request, redirect, url_for, render_template
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from werkzeug.security import check_password_hash
from werkzeug.utils import secure_filename
from file_handler import load_and_migrate, UserStore
import argparse
from admin import add_user_dialog
from pathlib import Path
from logger import logger

UPLOAD_DIR = Path("./uploads")
TEXT_FILE_DIR = Path("./results")

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
    return redirect(url_for("protected"))

@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("login"))

@app.route("/protected")
@login_required
def protected():
    return f"Hi {current_user.get_id()}, du bist eingeloggt."

@app.route("/upload", methods=["POST"])
@login_required
def upload():
    if "image" not in request.files:
        return "No file part", 400

    f = request.files["image"]
    if f.filename == "":
        return "No selected file", 400

    filename = secure_filename(f.filename)  # niemals ungeprüfte Dateinamen nutzen [web:157]
    save_path = UPLOAD_DIR / filename
    f.save(save_path)  # speichert auf disk [web:157]

    return f"Saved as {save_path.name}", 200

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



