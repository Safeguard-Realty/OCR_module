import PyPDF2
import easyocr
from PIL import Image, ImageEnhance, ImageOps
import cv2
import numpy as np
import re
import os
import io
import json

class OCRProcessor:
    def __init__(self, languages=["en"], use_gpu=True):
        self.reader = easyocr.Reader(languages, gpu=use_gpu)
    
    def preprocess_image(self, img_path):
        """Enhance image quality for OCR processing"""
        img = cv2.imread(img_path, cv2.IMREAD_GRAYSCALE)
        img = cv2.resize(img, None, fx=2, fy=2, interpolation=cv2.INTER_LINEAR)
        img = cv2.adaptiveThreshold(img, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
                                   cv2.THRESH_BINARY, 31, 15)
        img = Image.fromarray(img)
        img = ImageEnhance.Sharpness(img).enhance(2.0)
        img = ImageOps.autocontrast(img)
        return np.array(img)

    def process_image(self, image_path):
        """Extract text from image files"""
        processed_img = self.preprocess_image(image_path)
        return self.reader.readtext(processed_img, detail=0)

    def process_pdf(self, pdf_path):
        """Extract text from PDF files including embedded images"""
        text_content = []
        
        with open(pdf_path, 'rb') as file:
            pdf_reader = PyPDF2.PdfReader(file)
            for page in pdf_reader.pages:
                if (page_text := page.extract_text()):
                    text_content.append(page_text)
                
                if '/XObject' in (resources := page.get('/Resources', {})):
                    x_objects = resources['/XObject'].get_object()
                    for obj in x_objects:
                        if x_objects[obj]['/Subtype'] == '/Image':
                            with Image.open(io.BytesIO(x_objects[obj].get_data())) as img:
                                img.save("temp_img.png")
                                text_content.extend(self.process_image("temp_img.png"))
                                os.remove("temp_img.png")                                
        return text_content

class DataExtractor:
    @staticmethod
    def extract_fields(ocr_lines):
        """Enhanced extraction for Aadhaar, PAN, and Passport"""
        full_text = ' '.join(ocr_lines).upper()
        extracted = {
            "document_type": None,
            "identification_numbers": {},
            "personal_details": {
                "name": None,
                "father_name": None,
                "dob": None,
                "address": None,
                "gender": None
            },  
            "document_dates": [],
            "additional_info": {}
        }

        # Document type detection with priority
        if re.search(r'\b(UIDAI|AADHAAR|आधार)\b', full_text):
            extracted["document_type"] = "aadhaar"
        elif re.search(r'\b(PAN|PERMANENT ACCOUNT NUMBER)\b', full_text):
            extracted["document_type"] = "pan"
        elif re.search(r'\b(PASSPORT|REPUBLIC OF INDIA)\b', full_text):
            extracted["document_type"] = "passport"

        # Extract identification numbers
        id_patterns = {
            "aadhaar": r'\b(\d{4}\s?\d{4}\s?\d{4})\b',
            "pan": r'\b([A-Z]{5}\d{4}[A-Z])\b',
            "passport": r'\b([A-Z]\d{7})\b'
        }
        for id_type, pattern in id_patterns.items():
            if match := re.search(pattern, full_text):
                extracted["identification_numbers"][id_type] = match.group(1).replace(' ', '')

        # Document-specific extraction
        if extracted["document_type"] == "aadhaar":
            DataExtractor._extract_aadhaar_details(ocr_lines, extracted)
        elif extracted["document_type"] == "pan":
            DataExtractor._extract_pan_details(ocr_lines, extracted)
        elif extracted["document_type"] == "passport":
            DataExtractor._extract_passport_details(ocr_lines, extracted)

        # Common date extraction
        date_matches = re.findall(r'\d{2}[/\-\.]\d{2}[/\-\.]\d{4}', full_text)
        extracted["document_dates"] = list(set(date_matches))

        return extracted

    @staticmethod
    def _extract_aadhaar_details(lines, extracted):
        """Aadhaar specific field extraction"""
        name_pattern = r'^[A-Z\s]+$'
        address_lines = []
        capture_address = False

        for line in lines:
            line = line.strip().upper()
            # Name extraction
            if not extracted["personal_details"]["name"] and re.match(name_pattern, line):
                extracted["personal_details"]["name"] = line.title()
            
            # Address extraction
            if 'ADDRESS' in line:
                capture_address = True
                continue
            if capture_address and any(word in line for word in ['DOB', 'DATE', 'YEAR', 'MALE', 'FEMALE']):
                capture_address = False
            if capture_address and line:
                address_lines.append(line.title())
            
            # Gender extraction
            if 'MALE' in line:
                extracted["personal_details"]["gender"] = 'Male'
            elif 'FEMALE' in line:
                extracted["personal_details"]["gender"] = 'Female'

        if address_lines:
            extracted["personal_details"]["address"] = ' '.join(address_lines)

    @staticmethod
    def _extract_pan_details(lines, extracted):
        """PAN specific field extraction"""
        for line in lines:
            line = line.strip().upper()
            # Name extraction
            if re.match(r'^[A-Z\s]+$', line) and not extracted["personal_details"]["name"]:
                extracted["personal_details"]["name"] = line.title()
            
            # Father's name extraction
            if 'FATHER' in line:
                extracted["personal_details"]["father_name"] = line.split(':')[-1].strip().title()
            
            # Date of birth extraction
            if 'DOB' in line or 'DATE OF BIRTH' in line:
                if match := re.search(r'\d{2}/\d{2}/\d{4}', line):
                    extracted["personal_details"]["dob"] = match.group(0)

    @staticmethod
    def _extract_passport_details(lines, extracted):
        """Passport specific field extraction"""
        mrz_pattern = r'^P<([A-Z]+)<+(.+?)<<+'
        surname_found = False

        for i, line in enumerate(lines):
            line = line.strip().upper()
            # MRZ parsing
            if re.match(mrz_pattern, line):
                parts = re.split(r'<+', line)
                extracted["personal_details"]["surname"] = parts[1].replace('<', ' ').title()
                if len(parts) > 2:
                    extracted["personal_details"]["given_name"] = parts[2].replace('<', ' ').title()
            
            # Regular field parsing
            if 'SURNAME' in line:
                extracted["personal_details"]["surname"] = lines[i+1].strip().title()
            if 'GIVEN NAME' in line:
                extracted["personal_details"]["given_name"] = lines[i+1].strip().title()
            if 'PLACE OF BIRTH' in line:
                extracted["additional_info"]["pob"] = lines[i+1].strip().title()
            if 'PLACE OF ISSUE' in line:
                extracted["additional_info"]["poi"] = lines[i+1].strip().title()

        # Extract dates with context
        date_contexts = {
            'DATE OF BIRTH': 'dob',
            'DATE OF ISSUE': 'doi',
            'DATE OF EXPIRY': 'doe'
        }
        for i, line in enumerate(lines):
            for context, field in date_contexts.items():
                if context in line:
                    if match := re.search(r'\d{2}/\d{2}/\d{4}', line):
                        extracted["personal_details"][field] = match.group(0)
                    elif i+1 < len(lines):
                        if match := re.search(r'\d{2}/\d{2}/\d{4}', lines[i+1]):
                            extracted["personal_details"][field] = match.group(0)

class DocumentProcessor:
    def __init__(self):
        self.ocr = OCRProcessor()
        self.extractor = DataExtractor()
    
    def handle_file(self, file_path, output_path="output.json"):
        """Process different file types and save structured output"""
        try:
            file_ext = os.path.splitext(file_path)[1].lower()
            if file_ext == ".pdf":
                ocr_data = self.ocr.process_pdf(file_path)
            elif file_ext in (".png", ".jpg", ".jpeg", ".bmp"):
                ocr_data = self.ocr.process_image(file_path)
            else:
                raise ValueError("Unsupported file format")
            
            structured_data = self.extractor.extract_fields(ocr_data)
            
            with open(output_path, 'w') as f:
                json.dump(structured_data, f, indent=4, ensure_ascii=False)
            
            return structured_data
            
        except Exception as e:
            return {"error": str(e)}

# Usage Example
if __name__ == "__main__":
    processor = DocumentProcessor()
    
    # Test with different documents
    aadhaar_result = processor.handle_file("/Users/harshshivhare/OCR_module-1/Aadhar_test1.jpeg")
    # pan_result = processor.handle_file("/Users/harshshivhare/OCR_module-1/Aadhar_test1.jpeg")
    # passport_result = processor.handle_file("passport.jpg")
    
    print("Aadhaar Results:")
    print(json.dumps(aadhaar_result, indent=4))
    
    print("\nPAN Results:")
    # print(json.dumps(pan_result, indent=4))
    
    print("\nPassport Results:")
    # print(json.dumps(passport_result, indent=4))