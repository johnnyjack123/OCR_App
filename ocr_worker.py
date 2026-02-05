import threading
import time
from google_vision_api import prepare_ocr_process

task_queue = []

def worker():
    while task_queue:
        task = task_queue.pop(0)
        file_path = task["file_path_img"]
        start_ocr(file_path, task_queue)
    time.sleep(2)

def add_ocr_task(username, file_path_img):
    task_entry = {
        "username": username,
        "file_path_img": file_path_img
    }

    task_queue.append(task_entry)
    return

def start_worker():
    t = threading.Thread(target=worker, daemon=True)
    t.start()
    return

def start_ocr(file_path, task_queue):
    t = threading.Thread(target=prepare_ocr_process, args=(file_path, task_queue), daemon=True)
    t.start()#
    return