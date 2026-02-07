import json, ast

def extract_braced_block(s: str) -> str | None:
    start = s.find("{")
    if start == -1:
        return None

    depth = 0
    in_str = False
    quote = None
    escape = False

    for i in range(start, len(s)):
        ch = s[i]

        if in_str:
            if escape:
                escape = False
            elif ch == "\\":
                escape = True
            elif ch == quote:
                in_str = False
                quote = None
            continue

        if ch in ("'", '"'):
            in_str = True
            quote = ch
            continue

        if ch == "{":
            depth += 1
        elif ch == "}":
            depth -= 1
            if depth == 0:
                return s[start:i+1]

    return None  # keine passende schließende Klammer gefunden

def parse_llm_dict(text: str) -> dict:
    # 1) Falls das ganze schon JSON ist
    try:
        obj = json.loads(text)
        if isinstance(obj, dict):
            return obj
    except json.JSONDecodeError:
        pass

    # 2) Sonst: {...} Block extrahieren
    block = extract_braced_block(text)
    if block is None:
        raise ValueError("Kein {...}-Block gefunden")

    # 3) Erst JSON probieren (falls LLM doch korrektes JSON liefert)
    try:
        obj = json.loads(block)
        if isinstance(obj, dict):
            return obj
    except json.JSONDecodeError:
        pass

    # 4) Dann Python-Literal (dein Fall: {'title': ...})
    obj = ast.literal_eval(block)
    if not isinstance(obj, dict):
        raise ValueError("Extrahierter Block ist kein dict")
    return obj