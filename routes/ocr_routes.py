from fastapi import APIRouter, UploadFile
from controllers.ocr_controller import process_document_controller

router = APIRouter(tags=["OCR"])

@router.post("/process-document")
async def process_document(
    image_url: str,
    doc_type: str = "aadhar",  # Default to Aadhar processing
    max_retries: int =3
):
    return await process_document_controller(image_url, doc_type, max_retries)