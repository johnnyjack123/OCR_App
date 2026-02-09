from werkzeug.security import generate_password_hash

def generate_hash(password):
    password = generate_password_hash(password)
    return password