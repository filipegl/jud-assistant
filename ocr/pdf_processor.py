import pdfplumber
from tqdm import tqdm
from .ocr_engine import ocr_core
import os
import multiprocessing as mp
from PIL.Image import Image
from pdfplumber.page import Page
from functools import partial


def calculate_optimal_resolution(width: int | float, height: int | float) -> float:
    """
    Determines the resolution for OCR based on the image dimensions.
    If the image width/height is less than 2000 pixels, it scales the resolution accordingly.
    Also, it ensures that the resolution is set to a minimum of 72 DPI and a maximum of 250 DPI.
    Args:
        width: Width of the image.
        height: Height of the image.
    Returns:
        float: Resolution for OCR.
    """
    BASE_RESOLUTION = 72  # 72 means the width and height keep the same size
    if width < 2000:
        resolution = (2000 / width) * BASE_RESOLUTION
    elif height < 2000:
        resolution = (2000 / height) * BASE_RESOLUTION
    else:
        resolution = BASE_RESOLUTION
    return max(BASE_RESOLUTION, min(resolution, 250))  # Ensure resolution is between 72 and 250 DPI


def extract_images_from_pages(pages: list[Page]) -> list[Image]:
    """
    Extracts images from PDF pages.
    Args:
        pages (list[Page]): List of PDF pages.
    Returns:
        list[Image]: List of images extracted from the pages.
    """
    images: list[Image] = []
    for page in tqdm(pages, desc="OCR - Extracting images from PDF", unit="page"):
        resolution = calculate_optimal_resolution(page.width, page.height)
        images.append(page.to_image(antialias=True, resolution=resolution).original)
    return images


def extract_text_from_pdf(pdf_path_or_fp, lang, tessdata_dir) -> list[str]:
    """
    Extracts text from a PDF file using OCR.
    It converts each page to an image and applies OCR to extract text.
    This function uses multiprocessing for faster processing of larger PDFs.
    It also handles the case where the PDF has less than 3 pages by using a single process.
    Args:
        pdf_path_or_fp: Path to the PDF file or a file-like object.
        lang (str | None): Language for OCR.
        tessdata_dir (str | None): Directory for Tesseract data files
    Returns:
        list[str]: List of extracted text from each page of the PDF.
    """

    with pdfplumber.open(pdf_path_or_fp) as pdf:
        images = extract_images_from_pages(pdf.pages)
        num_pages = len(pdf.pages)
        texts: list[str] = []

        if num_pages >= 3:  # Use multiprocessing for larger PDFs
            num_processes = min(os.cpu_count(), num_pages)
            print(f"Using {num_processes} processes for OCR")
            with mp.Pool(processes=num_processes) as pool:
                ocr_core_partial = partial(ocr_core, lang=lang, tessdata_dir=tessdata_dir)
                results = list(
                    tqdm(
                        pool.imap(ocr_core_partial, images),
                        desc="OCR - Extracting text from PDF",
                        unit="page",
                        total=num_pages
                    )
                )
                texts.extend(results)
        else:
            for image in tqdm(images, desc="OCR - Extracting text from images", unit="page"):
                texts.append(ocr_core(image, lang=lang, tessdata_dir=tessdata_dir))

        return texts


def merge_texts_by_page(texts: list[str]) -> str:
    """
    Merges the extracted texts by page.
    Args:
        texts (list[str]): List of extracted text from each page of the PDF.
    Returns:
        str: Merged text with page numbers.
    """
    if len(texts) == 1:
        return texts[0]
    merged = ""
    for i, text in enumerate(texts):
        merged += f"Página {i+1}:\n{text}\n{'-'*8}\n"
    return merged
