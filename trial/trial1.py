import os
import re
import json
import cv2
import numpy as np
from PIL import Image, ImageEnhance
import easyocr
from typing import List, Dict, Optional


class ImagePreprocessor:
    """Handles image preprocessing for OCR optimization."""
    
    @staticmethod
    def preprocess(image_path: str) -> np.ndarray:
        """Preprocesses the image for OCR."""
        img = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
        
        # Resize and denoise
        img = cv2.resize(img, None, fx=2, fy=2, interpolation=cv2.INTER_CUBIC)
        img = cv2.medianBlur(img, 3)
        img = cv2.adaptiveThreshold(img, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 31, 12)
        
        # Enhance contrast and sharpness
        pil_img = Image.fromarray(img)
        pil_img = ImageEnhance.Contrast(pil_img).enhance(2.0)
        pil_img = ImageEnhance.Sharpness(pil_img).enhance(2.5)
        
        return np.array(pil_img)


class OCRProcessor:
    """Handles text extraction from images."""
    
    def __init__(self, languages: List[str] = ["en"], use_gpu: bool = True):
        self.reader = easyocr.Reader(languages, gpu=use_gpu)
    
    def process_image(self, image_path: str) -> List[str]:
        """Extracts text from an image."""
        processed_img = ImagePreprocessor.preprocess(image_path)
        results = self.reader.readtext(processed_img, paragraph=True, detail=1)
        extracted_text = [self._clean_text(result[1]) for result in results]
        return extracted_text

    @staticmethod
    def _clean_text(text: str) -> str:
        """Cleans OCR text."""
        text = re.sub(r'\s+', ' ', text)
        text = re.sub(r'[^\w\s/()-]', '', text)
        return text.strip()


class GovernmentIDParser:
    """Parses text from government IDs into structured data."""

    FIELD_PATTERNS = {
        "PAN": {
            "PAN Number": r'([A-Z]{5}\d{4}[A-Z])',
            "Name": r'([A-Z\s]+)\n[FATHER\'S|HUSBAND\'S NAME]',
            "Father's Name": r'FATHER\'S NAME\s*:\s*([A-Z\s]+)',
            "DOB": r'DATE OF BIRTH\s*:\s*(\d{2}/\d{2}/\d{4})'
        },
        "Passport": {
            "Passport Number": r'([A-Z]\d{7})',
            "Surname": r'SURNAME\s*:\s*([A-Z\s]+)',
            "Given Names": r'GIVEN NAMES\s*:\s*([A-Z\s]+)',
            "DOB": r'DATE OF BIRTH\s*:\s*(\d{2}/\d{2}/\d{4})',
            "Date of Expiry": r'DATE OF EXPIRY\s*:\s*(\d{2}/\d{2}/\d{4})',
            "Place of Issue": r'PLACE OF ISSUE\s*:\s*([A-Z\s]+)'
        },
        "Aadhaar": {

            "Name": r"^(.*)\s+(?:जन्म तिथि|DOB)",  # Match the name before DOB
            "DOB": r"(?:जन्म तिथि|DOB)[:\-]?\s*(\d{2}/\d{2}/\d{4})",
            "Gender": r"(पुरुष|महिला|Male|Female)",  # Match gender in Hindi/English
            "Aadhaar Number": r"(\d{4}\s\d{4}\s\d{4})"  # Match Aadhaar number
        }
    }

    def __init__(self, ocr_text: List[str], doc_type: str):
        self.ocr_text = ocr_text
        self.full_text = " ".join(ocr_text).upper()
        self.doc_type = doc_type
        self.parsed_data = self._parse_fields()

    def _parse_fields(self) -> Dict[str, Optional[str]]:
        """Parses fields using regex patterns."""
        result = {}
        patterns = self.FIELD_PATTERNS.get(self.doc_type, {})
        for field, pattern in patterns.items():
            match = re.search(pattern, self.full_text)
            if match:
                try:
                    result[field] = match.group(1).strip()
                except IndexError:
                    result[field] = None  # In case group(1) does not exist
                    print(f"Warning: Group not found for field '{field}'")
            else:
                result[field] = None  # Mark as missing if no match
        return result


import easyocr

class DocumentProcessor:
    def __init__(self):
        self.ocr_text = None

    def perform_ocr(self, image_path: str) -> str:
        """Performs OCR on the given image using EasyOCR."""
        reader = easyocr.Reader(['en'], gpu=False)  # Initialize EasyOCR
        ocr_result = reader.readtext(image_path)  # OCR results as list of [bbox, text, confidence]
        
        # Extract the text from the results and join it into a single string
        self.ocr_text = "\n".join([res[1] for res in ocr_result])
        return self.ocr_text


    def process_document(self, image_path: str, doc_type: str) -> Dict[str, Optional[str]]:
        """Processes the given document and parses its fields."""
        ocr_text = self.perform_ocr(image_path)
        print("Raw OCR Text:\n", ocr_text)  # Debugging step
        parser = GovernmentIDParser(ocr_text, doc_type)
        return parser.parsed_data



if __name__ == "__main__":
    processor = DocumentProcessor()
    
    # Paths to images
    pan_path = "/Users/harshshivhare/OCR_module-1/Pan_test1.jpeg"
    passport_path = "/Users/harshshivhare/OCR_module-1/Passport_test1.jpeg"

    aadhar_path = "/Users/harshshivhare/OCR_module-1/Aadhar_test2.jpeg"

    # aadhar_path = "/mnt/data/Aadhar_test2.jpeg"
    # aadhar_data = processor.process_document(aadhar_path, "Aadhaar")
    
    
    # Process Aadhaar Card
    aadhar_data = processor.process_document(aadhar_path, "Aadhaar")
    print("Aadhaar Card Data:", json.dumps(aadhar_data, indent=2))
    print("Raw OCR Text:", processor.ocr_text)
    
    # Process PAN Card
    pan_data = processor.process_document(pan_path, "PAN")
    print("PAN Card Data:", json.dumps(pan_data, indent=2))
    
    # Process Passport
    passport_data = processor.process_document(passport_path, "Passport")
    print("Passport Data:", json.dumps(passport_data, indent=2))
