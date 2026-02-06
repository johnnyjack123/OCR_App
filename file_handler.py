from __future__ import annotations
from pydantic import BaseModel, Field
from pathlib import Path
import json, os, tempfile
from threading import RLock
import datetime
import uuid
from logger import logger
import global_variables
import safe_shutil

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
    text_files: list = Field(default_factory=list)

class Program(BaseModel):
    version: float = 0.1
    api_renewal: str = ""
    cookie_key: str = ""
    llm_model: str = ""
    debug_mode: bool = False
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

# Creates and saves result .txt file
def create_result_file(final_file):
    file_name = str(uuid.uuid4())
    file_path = Path(global_variables.result_folder_path) / f"{file_name}.txt"
    #path = Path(f"{id_str}.txt")
    file_path.write_text(final_file, encoding="utf-8")
    return file_name

def save_result(result, task):
    print("Save result.")
    final_file = f"Corrected Output: \n \n {result['corrected_text']} \n \n Raw OCR Output: \n \n {result['raw_text']}"
    file_name = create_result_file(final_file)
    userdata = load_file()
    for user in userdata.users:
        if user.username == task["username"]:
            print("User found.")
            user.text_files.append(file_name)
            save_file(userdata)
            delete_image(task["file_path_img"])
            return
    logger.error("User not found.")
    return

def delete_image(image):
    #safe_shutil.remove(image)
    #TODO: Einkommentieren    
    return

def read_result(file_name):
    text = ""
    folder_path = Path(global_variables.result_folder_path)
    file_path = folder_path / f"{file_name}.txt"
    with Path(file_path).open("r", encoding="utf-8") as f:
        for line in f:
            text = text + line.rstrip("\n")
    return text