import openai
from typing import List, Dict, Any
from core.config import settings


class RAGChain:
    def __init__(self):
        self.client = openai.OpenAI(api_key=settings.openai_api_key)
        self.model = "gpt-4o-mini"
        self.system_prompt = """You are a helpful AI assistant that answers questions based on the provided context from uploaded documents. 

Instructions:
1. Use only the information provided in the context to answer questions
2. If the context doesn't contain enough information to answer the question, say so clearly
3. When referencing information, mention the source document and page number when possible
4. Be concise but thorough in your responses
5. If the question is not related to the provided context, politely redirect to document-related queries

Always ground your responses in the provided context and cite your sources."""
    
    def generate_response(
        self, 
        query: str, 
        context: str, 
        conversation_history: List[Dict[str, str]] = None
    ) -> str:
        messages = [
            {"role": "system", "content": self.system_prompt}
        ]
        
        # Add conversation history if provided (last 5 messages)
        if conversation_history:
            recent_history = conversation_history[-10:]  # Last 10 messages (5 turns)
            for msg in recent_history:
                if msg["role"] in ["user", "assistant"]:
                    messages.append({
                        "role": msg["role"],
                        "content": msg["content"]
                    })
        
        # Add current context and query
        user_message = f"""Context from uploaded documents:
{context}

Question: {query}"""
        
        messages.append({"role": "user", "content": user_message})
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                max_tokens=1000,
                temperature=0.1
            )
            
            return response.choices[0].message.content.strip()
        
        except Exception as e:
            print(f"Error generating response: {e}")
            return "I apologize, but I encountered an error while generating a response. Please try again."
    
    def extract_sources(self, retrieved_docs: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        sources = []
        seen_sources = set()
        
        for doc in retrieved_docs:
            metadata = doc["metadata"]
            source_key = f"{metadata['documentId']}_{metadata['page']}_{metadata['source']}"
            
            if source_key not in seen_sources:
                source = {
                    "documentId": metadata["documentId"],
                    "fileName": metadata["fileName"],
                    "page": metadata["page"],
                    "source": metadata["source"]
                }
                sources.append(source)
                seen_sources.add(source_key)
        
        return sources


rag_chain = RAGChain()