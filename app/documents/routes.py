from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form
from typing import Dict
import io
from core.security import get_current_user
from core.utils import generate_uuid, get_current_timestamp
from db.astra_client import astra_client
from db.s3_client import s3_client
from documents.processor import pdf_processor
from documents.summarizer import image_summarizer
from documents.embeddings import embeddings_service
from schemas.responses import DocumentUploadResponse, ErrorResponse

router = APIRouter(
    prefix="/documents", 
    tags=["Documents"],
    responses={
        400: {"model": ErrorResponse, "description": "Bad Request - Invalid file type or data"},
        401: {"model": ErrorResponse, "description": "Unauthorized - Invalid or missing token"},
        404: {"model": ErrorResponse, "description": "Session not found"},
        413: {"model": ErrorResponse, "description": "File too large"},
        500: {"model": ErrorResponse, "description": "Internal server error during processing"}
    }
)


@router.post(
    "/upload", 
    response_model=DocumentUploadResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Upload PDF Document",
    description="Upload a PDF document to a session for processing and indexing"
)
async def upload_document(
    sessionId: str = Form(..., description="Session ID where the document will be uploaded"),
    file: UploadFile = File(..., description="PDF file to upload (max size: 50MB)"),
    current_user: Dict[str, str] = Depends(get_current_user)
):
    """
    Upload and process a PDF document.
    
    This endpoint accepts a PDF file, uploads it to S3 storage, processes the content
    (both text and images), generates embeddings, and indexes everything for search.
    
    Args:
        sessionId: The session ID where the document belongs
        file: PDF file to upload (only .pdf files are accepted)
        current_user: Authenticated user information (injected by dependency)
        
    Returns:
        DocumentUploadResponse: Information about the uploaded and processed document
        
    Raises:
        HTTPException: 
            - 400: Invalid file type or session data
            - 404: Session not found or doesn't belong to user
            - 500: Error during file processing or storage
    """
    # Validate file type
    if not file.filename.lower().endswith('.pdf'):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only PDF files are supported"
        )
    
    # Verify session belongs to user
    session = astra_client.get_session(sessionId, current_user["userId"])
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Session not found or doesn't belong to user"
        )
    
    try:
        # Read PDF content
        pdf_content = await file.read()
        
        # Generate document ID and S3 key
        document_id = generate_uuid()
        s3_key = s3_client.generate_s3_key(
            current_user["userId"], 
            sessionId, 
            document_id, 
            file.filename
        )
        
        # Upload PDF to S3
        pdf_io = io.BytesIO(pdf_content)
        upload_success = s3_client.upload_file(pdf_io, s3_key, "application/pdf")
        
        if not upload_success:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to upload file to storage"
            )
        
        # Process PDF with PyMuPDF
        processed_pdf = pdf_processor.process_pdf(pdf_content)
        
        # Generate captions for images
        image_captions = []
        if processed_pdf["images_content"]:
            image_captions = image_summarizer.caption_multiple_images(
                processed_pdf["images_content"]
            )
        
        # Create embeddings and store in AstraDB
        chunks_indexed = embeddings_service.process_content_for_embeddings(
            processed_pdf["text_content"],
            image_captions,
            current_user["userId"],
            sessionId,
            document_id,
            file.filename
        )
        
        # Save document metadata
        document_doc = {
            "documentId": document_id,
            "userId": current_user["userId"],
            "sessionId": sessionId,
            "fileName": file.filename,
            "s3Key": s3_key,
            "uploadedAt": get_current_timestamp(),
            "pages": processed_pdf["total_pages"]
        }
        
        astra_client.create_document(document_doc)
        
        # Return response
        return DocumentUploadResponse(
            documentId=document_id,
            fileName=file.filename,
            s3Key=s3_key,
            pages=processed_pdf["total_pages"],
            chunksIndexed=chunks_indexed
        )
        
    except Exception as e:
        print(f"Error processing document: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error processing document"
        )