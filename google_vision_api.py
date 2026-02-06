from google.cloud import vision
import argparse
from pathlib import Path
from PIL import Image
import requests
from logger import logger
from file_handler import save_result, load_file

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
    print(f"Image path: {image_path}")
    client = vision.ImageAnnotatorClient()
    with open(image_path, 'rb') as image_file:
        content = image_file.read()
    image = vision.Image(content=content)

    # DOCUMENT_TEXT_DETECTION für Handschrift/Dokumente
    logger.info("Sent OCR request.")
    response = client.document_text_detection(image=image)
    texts = response.text_annotations[1:] if len(response.text_annotations) > 1 else []
    return '\n'.join([text.description for text in texts])


def correct_with_lm(text):
    url = "http://localhost:1234/v1/chat/completions"
    prompt = f"""Korrigiere OCR-Fehler in folgendem Text (Deutsch). Durch das OCR haben sich in dem Text Fehler eingeschlichen. Dabei handelt es sich um kleine Rechtschreibfehler,
    also das zum Beispiel nur ein Buchstabe falsch ist. Wenn dem so ist, korrigiere bitte dieses Wort richtig, oder auch, wenn mehrere Buchstaben falsch sind, aber ersichtlich ist. Wenn du ein Wort nicht sicher erkennen
    kannst, markiere ist zwischen jeweils zwei **, damit es bei mir im Markdowneditor hervorgehoben wird und ich es mit anschauen kann. Dabei ist ganz wichtig, dass du Wörter, wenn du sie nicht erkennst, nicht löschst, sondern 
    sie in die ** packsts, wie schon beschrieben. Schau unbedingt, dass der Satz dann am Ende auch Sinn ergibt. Schreibe nur den korrigierten Text zurück und keine weitere Antwort. Ergänze nur
    ganz oben an den Anfang die Wörter: Korrigierte Version.

            Hier ist der Text, den du überprüfen sollst:
            {text}
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
    corrected = correct_with_lm(text)
    return corrected

def process_worker(in_path):
    print(f"Performing OCR on document {in_path} to extract content.")
    text = simple_ocr_google(str(in_path))
    print("Trying to verify and correct text with generative AI.")
    corrected_text = verify_text(text)
    print("Success in correcting text.")
    return text, corrected_text

def prepare_ocr_process(in_path, task):
    text, corrected_text = process_worker(in_path)
    logger.info(f"Process finished.")
    result = {
        "raw_text": text,
        "corrected_text": corrected_text 
    }
    save_result(result, task)
    return
