from __future__ import annotations
from pydantic import BaseModel, Field
from pathlib import Path
import json, os, tempfile
from threading import RLock
import datetime
import uuid

file_path = Path("./userdata.json")
_lock = RLock()

class UserStore:
    def __init__(self, path: str | Path):
        self.path = Path(path)
        self._lock = RLock()

    def load(self) -> Program:
        with self._lock:
            return load_and_migrate()  # oder load_file, wenn du Migration beim Start machst

    def save(self, program: Program) -> None:
        with self._lock:
            save_file(program)

    def get_user(self, username: str) -> User | None:
        p = self.load()
        for u in p.users:
            if u.username == username:
                return u
        return None

class User(BaseModel):
    username: str = ""
    password_hash: str = ""
    text_files: list

class Program(BaseModel):
    version: float = 0.1
    api_renewal: str
    users: list[User] = Field(default_factory=list)

def atomic_write_text(text: str, encoding: str = "utf-8") -> None:
    file_path.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp = tempfile.mkstemp(dir=str(file_path.parent), prefix=file_path.name, suffix=".tmp")
    try:
        with os.fdopen(fd, "w", encoding=encoding) as f:
            f.write(text)
            f.flush()
            os.fsync(f.fileno())
        os.replace(tmp, file_path)
    finally:
        try:
            os.remove(tmp)
        except FileNotFoundError:
            pass

def load_file() -> Program:
    if not file_path.exists():
        return Program()

    raw = file_path.read_text(encoding="utf-8").strip()
    if not raw:              # Datei ist leer/whitespace
        return Program()

    try:
        data = json.loads(raw)
    except json.JSONDecodeError:
        # optional: kaputte Datei sichern
        # file_path.rename(file_path.with_suffix(".broken.json"))
        return Program()

    return Program.model_validate(data)

def save_file(program: Program) -> None:
    text = json.dumps(program.model_dump(mode="json"), indent=2, ensure_ascii=False)
    atomic_write_text(text)

def load_and_migrate() -> Program:
    before = file_path.read_text(encoding="utf-8") if file_path.exists() else None
    program = load_file()
    after = json.dumps(program.model_dump(mode="json"), indent=2, ensure_ascii=False)
    if before != after:
        atomic_write_text(after)
    return program

def add_user(userdata: dict) -> None:
    with _lock:  # Locking innerhalb eines Prozesses/Workers
        p = load_file()
        p.users.append(User(**userdata))
        save_file(p)

def create_result_file(final_file):
    id_obj = uuid.uuid4()     # UUID-Objekt
    id_str = str(id_obj)
    path = Path(f"{id_str}.txt")
    path.write_text(final_file, encoding="utf-8")
    return id_str