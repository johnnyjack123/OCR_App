from utils.file_handler import add_user, load_file
from werkzeug.security import generate_password_hash

def add_user_dialog():
    file = load_file()
    while True:
        username, password, password_confirm = get_credentials_dialog()
        if not username:
            print("Username empty.")
            continue

        if username == "exit": # Add some users until you set username to 'exit' followed by two presses on enter
            break

        if any(u.username == username for u in file.users):
            print("Username already exists.")
            continue

        if password != password_confirm:
            print("No password match.")
            continue

        if not password:
            print("Password empty.")
            continue

        password = generate_password_hash(password)
        userdata = {
            "username": username,
            "password_hash": password
            }
        add_user(userdata)
        print(f"Added user {username}")
    return

def get_credentials_dialog():
    username = input("Type in username: ")
    password = input("Type in password: ")
    password_confirm = input("Confirm password: ")
    return username, password, password_confirm