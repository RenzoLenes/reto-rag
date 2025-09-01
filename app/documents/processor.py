import fitz  # PyMuPDF
import io
from typing import List, Dict, Any, Tuple
from PIL import Image


class PDFProcessor:
    def __init__(self):
        pass
    
    def process_pdf(self, pdf_bytes: bytes) -> Dict[str, Any]:
        pdf_document = fitz.open(stream=pdf_bytes, filetype="pdf")
        
        text_content = []
        images_content = []
        
        for page_num in range(len(pdf_document)):
            page = pdf_document.load_page(page_num)
            
            # Extract text
            text = page.get_text("text")
            if text.strip():
                text_content.append({
                    "page": page_num + 1,
                    "content": text.strip(),
                    "source": "pdf_text"
                })
            
            # Extract images
            image_list = page.get_images(full=True)
            
            for img_index, img in enumerate(image_list):
                xref = img[0]
                pix = fitz.Pixmap(pdf_document, xref)
                
                # Convert to RGB if necessary
                if pix.n - pix.alpha < 4:  # GRAY or RGB
                    img_data = pix.tobytes("png")
                else:  # CMYK: convert to RGB first
                    pix1 = fitz.Pixmap(fitz.csRGB, pix)
                    img_data = pix1.tobytes("png")
                    pix1 = None
                
                pix = None
                
                # Create image metadata
                image_info = {
                    "page": page_num + 1,
                    "image_index": img_index,
                    "image_data": img_data,
                    "source": "image_caption"
                }
                
                images_content.append(image_info)
        
        # Get total pages before closing document
        total_pages = len(pdf_document)
        pdf_document.close()
        
        return {
            "text_content": text_content,
            "images_content": images_content,
            "total_pages": total_pages
        }


pdf_processor = PDFProcessor()