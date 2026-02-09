from google.cloud import vision
from pathlib import Path
from PIL import Image
import requests
from utils.logger import logger
from utils.file_handler import save_result, load_file
from utils.parse_json import parse_llm_dict
from gemini import correct_with_gemini
from sockets.sockets import send_document_history, socketio_push


def extract_document_structure(annotation):
    full_text = []
    if annotation:
        for page in annotation.pages:
            for block in page.blocks:
                block_text = ''
                for paragraph in block.paragraphs:
                    para_text = ''
                    for word in paragraph.words:
                        word_text = ''.join([symbol.text for symbol in word.symbols])
                        para_text += word_text + ' '
                    block_text += para_text.strip() + '\n\n'
                full_text.append(block_text.strip() + '\n\n---\n\n')  # Blöcke trennen
    return annotation.text if annotation else ''  # Fallback auf flachen Text

def advanced_ocr_google(image_path: str) -> str:
    client = vision.ImageAnnotatorClient()
    with open(image_path, 'rb') as image_file:
        content = image_file.read()
    image = vision.Image(content=content)

    # DOCUMENT_TEXT_DETECTION für Handschrift/Dokumente
    response = client.document_text_detection(image=image)
    annotation = response.full_text_annotation
    formatted_text = extract_document_structure(annotation)
    return formatted_text

def simple_ocr_google(image_path: str) -> str:
    client = vision.ImageAnnotatorClient()
    with open(image_path, 'rb') as f:
        content = f.read()
    
    image = vision.Image(content=content)
    logger.info("Sent OCR request.")

    response = client.document_text_detection(image=image)
    return response.full_text_annotation.text  # <--- wichtig


def correct_with_lm(text):
    url = "http://localhost:1234/v1/chat/completions"
    
    answer_structure = {"title": "title, choosen by you",
                        "text": "text, which you corrected"
                    }
    prompt = f"""Correct mistakes in the following text. The text could be in any language, so please try to recognize the 
    language and adapt your answer in this language. The Text will have several mistakes due to its a raw output from an OCR process.
    Your task is to find mistakes in the text, such as some missing letters in word or even find missing words, to ensure the text is 
    grammerly correct and makes sense. If you are not able to get the meaning of a word or a sentence mark it between two **, two on
    beginning, two on ending, so it gets highlightet in an markdown editor.
    In addition create an matching name to the topic of the file in the same language as the file is written. The name should be a short 
    one. It is very important that you only answer in the following json-structur, dont write any other stuff:
    {str(answer_structure)}. Here is the text: {text}. It is really important that your answer ONLY contents the Dictionary, following 
    the structure I sent you. Please dont send any text Outside of the dict. Please do not write any stuff like which tings you changed, 
    just the dictionary.
    """

    file = load_file()
    model = file.llm_model

    payload = {
        "model": model,
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.1,
        "max_tokens": 1024
    }

    resp = requests.post(url, json=payload)
    return resp.json()["choices"][0]["message"]["content"].strip()

def verify_text(text): # Correct text with large language modell provided by LM Studio
    corrected = correct_with_gemini(text)
    return corrected

def process_worker(task):
    print(f"Performing OCR on document {task['file_path_img']} to extract content.")
    text = simple_ocr_google(str(task['file_path_img']))
    socketio_push("progress", "Successfully finished OCR-process. Try to verify with AI.", task["username"])
    print("Trying to verify and correct text with generative AI.")
    corrected_text = verify_text(text)
    socketio_push("progress", "Successfully corrected text with AI.", task["username"])
    corrected_text_json = parse_llm_dict(corrected_text)
    print("Success in correcting text.")
    return text, corrected_text_json

def prepare_ocr_process(task):
    text, corrected_text_json = process_worker(task)
    logger.info(f"Process finished.")
    result = {
        "title": corrected_text_json["title"],
        "raw_text": text,
        "corrected_text": corrected_text_json["text"] 
    }
    save_result(result, task)
    send_document_history(task["username"])
    return
