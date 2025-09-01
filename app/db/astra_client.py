from astrapy import DataAPIClient
from astrapy.exceptions import CursorException
from astrapy.info import CollectionDefinition, CollectionVectorOptions
from astrapy.constants import VectorMetric
from typing import Dict, List, Any, Optional
from core.config import settings
import logging

logger = logging.getLogger(__name__)


class AstraDBClient:
    def __init__(self):
        self.client = DataAPIClient(settings.astra_db_application_token)
        self.database = self.client.get_database_by_api_endpoint(
            settings.astra_db_api_endpoint
        )
        
        # Ensure collections exist before initializing
        self._ensure_collections_exist()
        
        # Initialize collections
        self.users_collection = self.database.get_collection(
            settings.astra_db_collection_users
        )
        self.sessions_collection = self.database.get_collection(
            settings.astra_db_collection_sessions
        )
        self.documents_collection = self.database.get_collection(
            settings.astra_db_collection_documents
        )
        self.embeddings_collection = self.database.get_collection(
            settings.astra_db_collection_embeddings
        )
        self.messages_collection = self.database.get_collection(
            settings.astra_db_collection_messages
        )

    def _ensure_collections_exist(self):
        """Create collections if they don't exist"""
        
        # Collections that should NOT have vector support
        collections_config = [
            {
                "name": settings.astra_db_collection_users,
                "vector_config": None,
                "description": "Collection for user authentication and profile data"
            },
            {
                "name": settings.astra_db_collection_sessions,
                "vector_config": None,
                "description": "Collection for chat sessions"
            },
            {
                "name": settings.astra_db_collection_documents,
                "vector_config": None,
                "description": "Collection for document metadata"
            },
            {
                "name": settings.astra_db_collection_messages,
                "vector_config": None,
                "description": "Collection for chat message history"
            },
            {
                "name": settings.astra_db_collection_embeddings,
                "vector_config": {
                    "dimension": 1000,  # Reduced to fit AstraDB limits
                    "metric": VectorMetric.DOT_PRODUCT
                },
                "description": "Collection for document embeddings and vector search"
            }
        ]

        logger.info("Creating collections if they don't exist...")
        
        for config in collections_config:
            try:
                if "vector_config" in config and config["vector_config"]:
                    # Create vector collection for embeddings
                    collection_definition = CollectionDefinition(
                        vector=CollectionVectorOptions(
                            dimension=config["vector_config"]["dimension"],
                            metric=config["vector_config"]["metric"]
                        )
                    )
                    self.database.create_collection(
                        name=config["name"],
                        definition=collection_definition
                    )
                    logger.info(f"Created VECTOR collection: {config['name']} with {config['vector_config']['dimension']} dimensions")
                else:
                    # Create regular collection (no vectors)
                    self.database.create_collection(name=config["name"])
                    logger.info(f"Created REGULAR collection: {config['name']} (no vectors)")
                
            except Exception as e:
                if "already exists" in str(e).lower() or "collection_already_exists" in str(e).lower():
                    logger.info(f"Collection already exists: {config['name']}")
                    continue
                else:
                    logger.error(f"Error creating collection {config['name']}: {e}")
                    raise

    def create_user(self, user_data: Dict[str, Any]) -> Dict[str, Any]:
        result = self.users_collection.insert_one(user_data)
        return result

    def get_user_by_email(self, email: str) -> Optional[Dict[str, Any]]:
        result = self.users_collection.find_one({"email": email})
        return result

    def create_session(self, session_data: Dict[str, Any]) -> Dict[str, Any]:
        result = self.sessions_collection.insert_one(session_data)
        return result

    def get_user_sessions(self, user_id: str) -> List[Dict[str, Any]]:
        cursor = self.sessions_collection.find({"userId": user_id})
        return list(cursor)

    def get_session(self, session_id: str, user_id: str) -> Optional[Dict[str, Any]]:
        result = self.sessions_collection.find_one(
            {"sessionId": session_id, "userId": user_id}
        )
        return result

    def create_document(self, document_data: Dict[str, Any]) -> Dict[str, Any]:
        result = self.documents_collection.insert_one(document_data)
        return result

    def insert_embeddings(self, embeddings_data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        result = self.embeddings_collection.insert_many(embeddings_data)
        return result

    def vector_search(self, query_vector: List[float], filter_dict: Dict[str, Any], limit: int = 5) -> List[Dict[str, Any]]:
        cursor = self.embeddings_collection.find(
            filter=filter_dict
        )
        return list(cursor)

    def create_message(self, message_data: Dict[str, Any]) -> Dict[str, Any]:
        result = self.messages_collection.insert_one(message_data)
        return result

    def get_session_messages(self, session_id: str, user_id: str) -> List[Dict[str, Any]]:
        cursor = self.messages_collection.find(
            {"sessionId": session_id, "userId": user_id}
        ).sort({"createdAt": 1})
        return list(cursor)


# Global instance
astra_client = AstraDBClient()