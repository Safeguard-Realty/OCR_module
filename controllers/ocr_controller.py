from fastapi import HTTPException
import time
import asyncio
from models.ocr_model import AadharExtraction, PANExtraction, PassportExtraction
from services.ocr_service import extract_aadhar_details, extract_pan_card_details, extract_passport_details
from utils.parsers import parse_aadhar_details, parse_pan_details, parse_passport_details
import logging

# Configure logging
logger = logging.getLogger(__name__)
REQUIRED_FIELDS = {
    'aadhar': ['Name', 'Date_Of_Birth', 'Gender', 'Aadhar_No', 'Address'],
    'pan': ['panCardNumber', 'name', 'fatherName', 'dateOfBirth'],
    'passport': ['Passport_No', 'Surname', 'Given_Name', 'Nationality', 'Sex',
                 'Date_of_Birth', 'Place_of_Birth', 'Date_of_Issue',
                 'Date_of_Expiry', 'Place_of_Issue']
}

async def process_document_controller(image_url: str, doc_type: str, max_retries=3):
    """Main processing function with retry mechanism"""
    best_result = None
    retries = 0
    last_error = None
    
    while retries <= max_retries:
        try:
            logger.info(f"Attempt {retries+1}/{max_retries+1} for {doc_type} processing")

            # Extract and parse
            if doc_type == 'aadhar':
                raw = extract_aadhar_details(image_url)
                parsed = parse_aadhar_details(raw)
            elif doc_type == 'pan':
                raw = extract_pan_card_details(image_url)
                parsed = parse_pan_details(raw)
            elif doc_type == 'passport':
                raw = extract_passport_details(image_url)
                parsed = parse_passport_details(raw)
            else:
                raise HTTPException(status_code=400, detail="Unsupported document type")

            # Validate parsed data
            current_result = {
                "document_type": doc_type,
                # "raw_output": raw,
                "parsed_data": parsed
            }

            # Check required fields
            required = REQUIRED_FIELDS[doc_type]
            missing_fields = [field for field in required if not parsed.get(field, '')]
            
            if not missing_fields:
                logger.info("All required fields extracted successfully")
                return current_result

            logger.warning(f"Missing fields: {', '.join(missing_fields)}")
            
            # Update best result if better than previous
            if not best_result or (sum(len(v) for v in parsed.values()) > 
                                 sum(len(v) for v in best_result['parsed_data'].values())):
                best_result = current_result

            retries += 1
            if retries <= max_retries:
                await asyncio.sleep(1)  # Non-blocking sleep for async

        except Exception as e:
            logger.error(f"Attempt {retries+1} failed: {str(e)}")
            last_error = str(e)
            retries += 1
            if retries <= max_retries:
                await asyncio.sleep(1)

    # Final error handling
    error_detail = "Failed to process document after maximum retries"
    if last_error:
        error_detail += f". Last error: {last_error}"
    
    if best_result:
        logger.warning("Returning partial results with missing fields")
        missing = [f for f in REQUIRED_FIELDS[doc_type] if not best_result['parsed_data'].get(f)]
        error_detail += f". Missing fields: {', '.join(missing)}"
        raise HTTPException(
            status_code=422,
            detail=error_detail,
            headers={"X-Error-Type": "Partial Extraction"},
        )
    
    logger.error("Complete processing failure")
    raise HTTPException(
        status_code=500,
        detail=error_detail,
        headers={"X-Error-Type": "Processing Failure"},
    )