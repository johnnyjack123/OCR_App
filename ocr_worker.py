import threading
import time
from google_vision_api import prepare_ocr_process
from utils.logger import logger
from pathlib import Path
import utils.global_variables as global_variables

task_queue = []

def worker():
    while True:
        while task_queue != []:
            task = task_queue.pop(0)
            logger.info(f"Task: {task}")
            start_ocr(task)
        time.sleep(2)

def add_ocr_task(username, file_name):
    file_path_img = Path(global_variables.upload_folder_path) / file_name
    task_entry = {
        "username": username,
        "file_path_img": file_path_img
    }

    task_queue.append(task_entry)
    print(f"Task_Queue: {task_queue}")
    return

def start_worker():
    print("Start worker.")
    t = threading.Thread(target=worker, daemon=True)
    t.start()
    return

def start_ocr(task):
    t = threading.Thread(target=prepare_ocr_process, args=(task,), daemon=True)
    t.start()#
    return