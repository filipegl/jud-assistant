from PIL import Image
from .ocr_engine import ocr_core


def extract_text_from_image(image_path, lang: str | None, tessdata_dir: str | None) -> str:
    """
    Extracts text from an image using OCR.
    Args:
        image_path (str): Path to the image file.
        lang (str | None): Language for OCR.
        tessdata_dir (str | None): Directory for Tesseract data files
    Returns:
        str: Extracted text from the image.
    """
    image = Image.open(image_path)
    text: str = ocr_core(image, lang=lang, tessdata_dir=tessdata_dir)
    return text
