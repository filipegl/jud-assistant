import pytesseract
from PIL import Image
import os

OCR_LANG = os.getenv("OCR_LANG", "eng")
TESSDATA_DIR = os.getenv("TESSDATA_DIR", None)


def ocr_core(image: Image, lang, tessdata_dir):
    """
    Applies OCR to the given image using Tesseract.
    Args:
        image (Image): The image to process.
        lang (str): Language for OCR.
        tessdata_dir (str | None): Directory for Tesseract data files
    Returns:
        str: Extracted text from the image.
    """

    if lang is None:
        lang = OCR_LANG
    if tessdata_dir is None:
        tessdata_dir = TESSDATA_DIR

    config = f'--tessdata-dir {tessdata_dir}' if tessdata_dir else ''
    text: str = pytesseract.image_to_string(image, lang=lang, config=config)
    return text
