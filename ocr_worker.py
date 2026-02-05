import threading
import time
import global_variables
from google_vision_api import prepare_ocr_process
from file_handler import create_result_file, load_file, save_file

def worker():
    task_queue = global_variables.task_queue
    while task_queue:
        task = task_queue.pop(0)
        file_path = task["file_path_img"]
        result = prepare_ocr_process(file_path)
        final_file = f"Raw OCR Output: \n \n {result["raw_text"]} \n \n Corrected Output: \n \n {result["corrected_text"]}"
        file_name = create_result_file(final_file)
        userdata = load_file()
        for user in userdata.users:
            if user == task["username"]:
                user.text_files.append(file_name)
                save_file(userdata)
    time.sleep(2)

def add_ocr_task():
    pass

def start_worker():
    t = threading.Thread(target=worker, args=(1, "x"), daemon=True)
    t.start()