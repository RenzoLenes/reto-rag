import openai
from typing import List, Dict, Any
from core.config import settings
from db.astra_client import astra_client


class RAGRetriever:
    def __init__(self):
        self.client = openai.OpenAI(api_key=settings.openai_api_key)
        self.embedding_model = "text-embedding-3-small"
        self.top_k = 5
    
    def create_query_embedding(self, query: str) -> List[float]:
        try:
            response = self.client.embeddings.create(
                model=self.embedding_model,
                dimensions=1000,
                input=query
            )
            return response.data[0].embedding
        except Exception as e:
            print(f"Error creating query embedding: {e}")
            return []
    
    def retrieve_relevant_docs(
        self, 
        query: str, 
        user_id: str, 
        session_id: str,
        top_k: int = None
    ) -> List[Dict[str, Any]]:
        if top_k is None:
            top_k = self.top_k
        
        # Create embedding for the query
        query_embedding = self.create_query_embedding(query)
        
        if not query_embedding:
            return []
        
        # Filter by userId and sessionId
        filter_dict = {
            "$and": [
                {"metadata.userId": user_id},
                {"metadata.sessionId": session_id}
            ]
        }

        # Debug logging
        print(f"🔍 Query: {query}")
        print(f"🆔 User ID: {user_id}")
        print(f"📝 Session ID: {session_id}")
        print(f"🎯 Filter: {filter_dict}")
        print(f"📏 Query embedding length: {len(query_embedding)}")

        # Perform vector search
        results = astra_client.vector_search(
            query_vector=query_embedding,
            filter_dict=filter_dict,
            limit=top_k
        )
        
        print(f"📊 Search results count: {len(results)}")
        if results:
            print(f"✅ First result sample: {results[0].get('content', 'N/A')[:100]}...")
        else:
            print("❌ No results found")
        
        # Format results for RAG
        formatted_results = []
        for result in results:
            formatted_doc = {
                "content": result["content"],
                "metadata": result["metadata"],
                "similarity": result.get("$similarity", 0.0)
            }
            formatted_results.append(formatted_doc)
        
        return formatted_results
    
    def format_context_for_prompt(self, retrieved_docs: List[Dict[str, Any]]) -> str:
        if not retrieved_docs:
            return "No relevant information found in the uploaded documents."
        
        context_parts = []
        
        for i, doc in enumerate(retrieved_docs, 1):
            metadata = doc["metadata"]
            source_info = f"[Source: {metadata['fileName']}, Page {metadata['page']}, {metadata['source']}]"
            context_parts.append(f"{i}. {doc['content']}\n{source_info}")
        
        return "\n\n".join(context_parts)


rag_retriever = RAGRetriever()