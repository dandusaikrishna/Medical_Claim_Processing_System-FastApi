import io
from typing import List
from fastapi import UploadFile

async def read_file_content(file: UploadFile) -> bytes:
    """
    Read the content of an uploaded file asynchronously.
    """
    return await file.read()

def save_file_to_disk(file_content: bytes, filename: str, directory: str = "uploads") -> str:
    """
    Save file content to disk under the specified directory.
    Returns the saved file path.
    """
    import os
    if not os.path.exists(directory):
        os.makedirs(directory)
    file_path = os.path.join(directory, filename)
    with open(file_path, "wb") as f:
        f.write(file_content)
    return file_path

def validate_pdf_files(files: List[UploadFile]) -> bool:
    """
    Validate that all uploaded files are PDFs.
    """
    for file in files:
        if not file.filename.lower().endswith(".pdf"):
            return False
    return True
