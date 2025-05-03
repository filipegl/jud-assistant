from pathlib import Path
from streamlit.runtime.uploaded_file_manager import UploadedFile
from .pdf_processor import extract_text_from_pdf, merge_texts_by_page
from .image_processor import extract_text_from_image


def is_pdf(file_path: str | Path) -> bool:
    return str(file_path).lower().endswith(".pdf")


def is_image(file_path: str | Path) -> bool:
    return any(str(file_path).lower().endswith(ext) for ext in ['.jpg', '.jpeg', '.png'])


def is_docx(file_path: str | Path) -> bool:
    return str(file_path).lower().endswith('.docx')


def extract_text(file_path: str | Path | UploadedFile, lang=None, tessdata_dir=None) -> str:
    """
    Extracts text from a file (PDF, image, or DOCX).

    Args:
        file_path (str | Path | UploadedFile): Path to the file or an UploadedFile object.
        lang (str, optional): Language code for OCR processing. Defaults to None.
        tessdata_dir (str, optional): Path to the Tesseract data directory. Defaults to None.

    Returns:
        str: Extracted text.

    Raises:
        FileNotFoundError: If the file does not exist.
        ValueError: If the file type is unsupported.
        NotImplementedError: If the file type is DOCX (not yet implemented).
    """
    if isinstance(file_path, UploadedFile):
        # Handle Streamlit's UploadedFile
        file_name = file_path.name
    else:
        file_path = Path(file_path)
        file_name = str(file_path)
        if not file_path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")

    if is_pdf(file_name):
        texts = extract_text_from_pdf(file_path, lang=lang, tessdata_dir=tessdata_dir)
        return merge_texts_by_page(texts)
    elif is_image(file_name):
        return extract_text_from_image(file_path, lang=lang, tessdata_dir=tessdata_dir)
    elif is_docx(file_name):
        raise NotImplementedError("DOCX file extraction is not implemented yet.")
    else:
        raise ValueError(f"Unsupported file type: {file_path}")
