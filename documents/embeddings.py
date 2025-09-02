import openai
from typing import List, Dict, Any
from langchain.text_splitter import RecursiveCharacterTextSplitter
from core.config import settings
from core.utils import generate_uuid
from db.astra_client import astra_client


# Constants for text splitting
CHUNK_SIZE = 1000
CHUNK_OVERLAP = 150


class EmbeddingsService:
    def __init__(self):
        self.client = openai.OpenAI(api_key=settings.openai_api_key)
        self.embedding_model = "text-embedding-3-small"
        
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=CHUNK_SIZE,
            chunk_overlap=CHUNK_OVERLAP,
            length_function=len,
            separators=["\n\n", "\n", " ", ""]
        )
    
    def create_embedding(self, text: str) -> List[float]:
        try:
            response = self.client.embeddings.create(
                model=self.embedding_model,
                input=text,
                dimensions=1000,  # Reduce from 1536 to 1000 to fit AstraDB limits
                encoding_format="float"
            )
            return response.data[0].embedding
        except Exception as e:
            print(f"Error creating embedding: {e}")
            return []
    
    def split_text(self, text: str) -> List[str]:
        return self.text_splitter.split_text(text)
    
    def process_content_for_embeddings(
        self, 
        text_content: List[Dict[str, Any]], 
        image_captions: List[Dict[str, Any]],
        user_id: str,
        session_id: str,
        document_id: str,
        file_name: str
    ) -> int:
        embeddings_data = []
        
        # Process text content
        for text_item in text_content:
            text_chunks = self.split_text(text_item["content"])
            
            for chunk in text_chunks:
                if chunk.strip():
                    embedding = self.create_embedding(chunk)
                    
                    if embedding:  # Only add if embedding was successful
                        embedding_doc = {
                            "id": generate_uuid(),
                            "content": chunk,
                            "embedding": embedding,
                            "metadata": {
                                "userId": user_id,
                                "sessionId": session_id,
                                "documentId": document_id,
                                "source": text_item["source"],
                                "page": text_item["page"],
                                "fileName": file_name
                            }
                        }
                        embeddings_data.append(embedding_doc)
        
        # Process image captions
        for caption_item in image_captions:
            if caption_item["caption"].strip():
                embedding = self.create_embedding(caption_item["caption"])
                
                if embedding:  # Only add if embedding was successful
                    embedding_doc = {
                        "id": generate_uuid(),
                        "content": caption_item["caption"],
                        "embedding": embedding,
                        "metadata": {
                            "userId": user_id,
                            "sessionId": session_id,
                            "documentId": document_id,
                            "source": caption_item["source"],
                            "page": caption_item["page"],
                            "fileName": file_name
                        }
                    }
                    embeddings_data.append(embedding_doc)
        
        # Insert all embeddings into AstraDB
        if embeddings_data:
            astra_client.insert_embeddings(embeddings_data)
        
        return len(embeddings_data)


embeddings_service = EmbeddingsService()