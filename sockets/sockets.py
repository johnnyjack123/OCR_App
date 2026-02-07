from flask import request
from flask_login import current_user
from flask_socketio import SocketIO, emit, join_room, leave_room
from .extensions import socketio
from utils.file_handler import load_file, read_result

def user_room(user_id: str) -> str:
    # stabiler Raumname pro User
    return f"user:{user_id}"

@socketio.on("connect")
def on_connect():
    username = current_user.get_id()
    # optional: Verbindungen ohne Login sofort ablehnen
    if not current_user.is_authenticated:
        return False  # Connection rejected
    room = user_room(username)
    join_room(room)
    emit("ws_ready", {"room": room, "user": username}, to=request.sid)
    emit("test", {"msg": "hello after join"}, to=f"user:{username}")
    send_document_history(username)

@socketio.on("disconnect")
def on_disconnect():
    # leave_room ist optional, SocketIO räumt Rooms beim Disconnect i.d.R. auf
    if current_user.is_authenticated:
        leave_room(user_room(current_user.get_id()))

@socketio.on("ping_me")
def ping_me(data):
    # Beispiel: Antwort geht nur an den User-Raum
    emit("pong", {"ok": True, "echo": data}, to=user_room(current_user.get_id()))

def send_document_history(username):
    files = []
    file_content = []
    file = load_file()
    users = file.users
    for user in users:
        if user.username == username:
            files = user.text_files
    if files != []:
        for file in files:
            content = read_result(file)
            file_content.append({file: content})
        socketio_push("document_history", file_content, username)

def socketio_push(channel, message, username):
    print(f"Socketio push to channel {channel} with msg {message}")
    socketio.emit(channel, message, to=user_room(username))