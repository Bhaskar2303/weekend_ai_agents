import os
import json
import PyPDF2
from pathlib import Path


def load_memory(memory_file: str) -> list:
    if os.path.exists(memory_file):
        with open(memory_file, 'r') as f:
            return json.load(f).get("learnings", [])
    return []


def save_memory(memory: list, memory_file: str):
    with open(memory_file, 'w') as f:
        json.dump({"learnings": memory}, f, indent=2)


def validate_path(pdf_path: str, allowed_dir: Path) -> Path:
    path = Path(pdf_path).resolve()
    if not str(path).startswith(str(allowed_dir)):
        raise ValueError("Access denied: Path is outside allowed directory")
    return path


def format_memory_for_context(memory: list) -> str:
    if not memory:
        return "No previous learning"
    memory_text = "Learned Patterns:\n"
    for learning in memory[-3:]:
        memory_text += f"-{learning['correction']}\n"
    return memory_text


# local  - NO MITM
def extract_text_from_pdf(pdf_path: str, allowed_dir: Path) -> str:
    path = validate_path(pdf_path, allowed_dir)
    with open(path, 'rb') as file:
        reader = PyPDF2.PdfReader(file)
        text_parts = [page.extract_text() for page in reader.pages]
    return "\n".join(text_parts)
