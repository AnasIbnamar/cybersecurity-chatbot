import re


def sanitize_input(text: str, max_length: int = 2000) -> str:
    if not isinstance(text, str):
        return ""
    text = text.strip()
    text = text[:max_length]
    text = text.replace('\x00', '')
    # Remove control characters except newlines and tabs
    text = re.sub(r'[\x01-\x08\x0b\x0c\x0e-\x1f\x7f]', '', text)
    return text
