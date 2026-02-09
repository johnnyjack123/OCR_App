from werkzeug.security import generate_password_hash
from utils.file_handler import load_file, save_file
from utils.logger import logger
import secrets
import string

def generate_hash(password):
    password = generate_password_hash(password)
    return password

def set_cookie_key():
    file = load_file()
    if file.cookie_key == "":
        logger.info(f"Create cookie key.")
        alphabet = string.ascii_letters + string.digits  # A-Z a-z 0-9
        token = "".join(secrets.choice(alphabet) for _ in range(32))
        file.cookie_key = token
        save_file(file)
    return