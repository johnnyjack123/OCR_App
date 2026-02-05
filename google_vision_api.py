from google.cloud import vision
import argparse
from pathlib import Path
from PIL import Image
import requests

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
    with open(image_path, 'rb') as image_file:
        content = image_file.read()
    image = vision.Image(content=content)

    # DOCUMENT_TEXT_DETECTION für Handschrift/Dokumente
    response = client.document_text_detection(image=image)
    texts = response.text_annotations[1:] if len(response.text_annotations) > 1 else []
    return '\n'.join([text.description for text in texts])


def correct_with_lm(text, model="openai/gpt-oss-20b"):
    url = "http://localhost:1234/v1/chat/completions"
    prompt = f"""Korrigiere OCR-Fehler in folgendem Text (Deutsch). Durch das OCR haben sich in dem Text Fehler eingeschlichen. Dabei handelt es sich um kleine Rechtschreibfehler,
    also das zum Beispiel nur ein Buchstabe falsch ist. Wenn dem so ist, korrigiere bitte dieses Wort richtig, oder auch, wenn mehrere Buchstaben falsch sind, aber ersichtlich ist. Wenn du ein Wort nicht sicher erkennen
    kannst, markiere ist zwischen jeweils zwei **, damit es bei mir im Markdowneditor hervorgehoben wird und ich es mit anschauen kann. Dabei ist ganz wichtig, dass du Wörter, wenn du sie nicht erkennst, nicht löschst, sondern 
    sie in die ** packsts, wie schon beschrieben. Schau unbedingt, dass der Satz dann am Ende auch Sinn ergibt. Schreibe nur den korrigierten Text zurück und keine weitere Antwort. Ergänze nur
    ganz oben an den Anfang die Wörter: Korrigierte Version.

            Hier ist der Text, den du überprüfen sollst:
            {text}
"""

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

def process_worker(in_path, out_dir):
    print(f"Performing OCR on document {in_path} to extract content.")
    text = simple_ocr_google(str(in_path))
    print("Trying to verify and correct text with generative AI.")
    corrected_text = verify_text(text)
    out_file = out_dir / f"{in_path.stem}.txt"
    out_file.write_text(corrected_text, encoding="utf-8")

def grab_arguments():
    parser = argparse.ArgumentParser()
    parser.add_argument("input")
    parser.add_argument("-o", "--out", default="gvision_out")
    args = parser.parse_args()

    in_path = Path(args.input)
    out_dir = Path(args.out)
    out_dir.mkdir(exist_ok=True)
    return in_path, out_dir

def prepare_ocr_process():
    in_path, out_dir = grab_arguments()
    quantity_files = 0
    count = 0
    if in_path.is_dir():
        for file in in_path.iterdir():
            quantity_files = quantity_files + 1
        for file in in_path.iterdir():
            if file.is_file():
                process_worker(file, out_dir)
                count = count + 1
        print(f"Process finished. Your text files are saved in {out_dir}. {count} of {quantity_files} files done.")
    else:
        process_worker(in_path, out_dir)
        print(f"Process finished. Your text file is saved in {out_dir}")

if __name__ == "__main__":
    prepare_ocr_process()
