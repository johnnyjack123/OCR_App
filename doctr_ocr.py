#!/usr/bin/env python3
import argparse
from pathlib import Path
import torch
import cv2
from doctr.io import DocumentFile
from doctr.models import ocr_predictor

def iter_images(path: Path):
    exts = {".jpg", ".jpeg", ".png", ".webp", ".tif", ".tiff", ".bmp"}
    if path.is_dir():
        for p in sorted(path.rglob("*")):
            if p.suffix.lower() in exts:
                yield p
    else:
        yield path

def preprocess_image(img_path: Path) -> str:
    """Kontrast/Skalierung für bessere OCR"""
    img = cv2.imread(str(img_path), cv2.IMREAD_GRAYSCALE)
    img = cv2.convertScaleAbs(img, alpha=1.2, beta=10)  # Kontrast
    img = cv2.resize(img, (0, 0), fx=0.8, fy=0.8)      # Etwas kleiner
    temp_path = img_path.parent / f"temp_{img_path.stem}.jpg"
    cv2.imwrite(str(temp_path), img)
    return str(temp_path)

def ocr_one(model, orig_path: Path) -> str:
    temp_img = preprocess_image(orig_path)
    try:
        doc = DocumentFile.from_images(temp_img)
        result = model(doc)
        lines = []
        for page in result.pages:
            for block in page.blocks:
                for line in block.lines:
                    line_text = " ".join([word.value for word in line.words])
                    if line_text.strip():
                        lines.append(line_text.strip())
        return "\n".join(lines)
    finally:
        Path(temp_img).unlink()  # Temp löschen

def main():
    parser = argparse.ArgumentParser(description="docTR OCR mit Preprocessing")
    parser.add_argument("input", help="Bild oder Ordner")
    parser.add_argument("-o", "--out", default="ocr_out", help="Output-Ordner")
    args = parser.parse_args()

    in_path = Path(args.input)
    out_dir = Path(args.out)
    out_dir.mkdir(parents=True, exist_ok=True)

    print("Lade docTR-Modell...")
    model = ocr_predictor(det_arch='db_resnet50', reco_arch='crnn_vgg16_bn', pretrained=True)

    print("Starte OCR...")
    for orig_img in iter_images(in_path):
        txt = ocr_one(model, orig_img)
        out_file = out_dir / f"{orig_img.stem}.txt"
        out_file.write_text(txt, encoding="utf-8")
        print(f"✓ {out_file.name} ({len(txt)} Zeichen)")

if __name__ == "__main__":
    main()
