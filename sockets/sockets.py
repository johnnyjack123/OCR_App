from flask import request
from flask_login import current_user
from flask_socketio import SocketIO, emit, join_room, leave_room
from .extensions import socketio

def user_room(user_id: str) -> str:
    # stabiler Raumname pro User
    return f"user:{user_id}"

@socketio.on("connect")
def on_connect():
    # optional: Verbindungen ohne Login sofort ablehnen
    if not current_user.is_authenticated:
        return False  # Connection rejected

    room = user_room(current_user.get_id())
    join_room(room)
    emit("ws_ready", {"room": room, "user": current_user.get_id()}, to=request.sid)

@socketio.on("disconnect")
def on_disconnect():
    # leave_room ist optional, SocketIO räumt Rooms beim Disconnect i.d.R. auf
    if current_user.is_authenticated:
        leave_room(user_room(current_user.get_id()))

@socketio.on("ping_me")
def ping_me(data):
    # Beispiel: Antwort geht nur an den User-Raum
    emit("pong", {"ok": True, "echo": data}, to=user_room(current_user.get_id()))

def socketio_push(channel, message):
    emit(channel, message, to=user_room(current_user.get_id()))