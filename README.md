# RAG Chatbot - Multimodal Backend

A FastAPI backend for a multimodal RAG (Retrieval-Augmented Generation) chatbot that processes PDFs containing text and images. The system extracts text and images from PDFs, generates captions for images using OpenAI GPT-4o-mini, vectorizes everything as text using OpenAI embeddings, and provides filtered retrieval by userId and sessionId.

## Features

- **Multimodal PDF Processing**: Extract both text and images from PDF documents using PyMuPDF
- **Image Captioning**: Generate descriptions for images using OpenAI GPT-4o-mini
- **Vector Storage**: Store embeddings in AstraDB with metadata filtering
- **Multi-tenant**: Complete user isolation with JWT authentication
- **RAG Chat**: Contextual responses using retrieved document chunks
- **S3 Storage**: PDF files stored in Amazon S3
- **Conversation History**: Persistent chat history per session

## Technology Stack

- **Backend**: Python 3.11+, FastAPI
- **Authentication**: JWT (no refresh tokens)
- **Storage**: Amazon S3 (PDFs), AstraDB (vectors, metadata, users)
- **PDF Processing**: PyMuPDF (fitz)
- **AI/ML**: OpenAI (GPT-4o-mini for captions, text-embedding-3-small for vectors)
- **Framework**: LangChain for RAG pipeline

## Project Structure

```
rag-chatbot/
├─ app/
│  ├─ main.py                  # FastAPI application
│  ├─ core/
│  │  ├─ config.py            # Environment configuration
│  │  ├─ security.py          # JWT authentication
│  │  └─ utils.py             # Utility functions
│  ├─ db/
│  │  ├─ astra_client.py      # AstraDB client and operations
│  │  └─ s3_client.py         # Amazon S3 client
│  ├─ auth/
│  │  ├─ routes.py            # Authentication endpoints
│  │  ├─ service.py           # Auth business logic
│  │  └─ models.py            # Auth Pydantic models
│  ├─ sessions/
│  │  ├─ routes.py            # Session management endpoints
│  │  └─ models.py            # Session Pydantic models
│  ├─ documents/
│  │  ├─ routes.py            # Document upload endpoint
│  │  ├─ processor.py         # PDF text/image extraction
│  │  ├─ summarizer.py        # Image captioning service
│  │  └─ embeddings.py        # Text splitting and embedding
│  ├─ chat/
│  │  ├─ routes.py            # Chat query endpoint
│  │  ├─ retriever.py         # RAG retrieval logic
│  │  └─ rag_chain.py         # Response generation
│  └─ schemas/
│     └─ common.py            # Shared Pydantic models
├─ requirements.txt
├─ .env                       # Environment variables (not committed)
└─ README.md
```

## Setup Instructions

### 1. Prerequisites

- Python 3.11 or higher
- AstraDB account with vector search capabilities
- AWS S3 bucket
- OpenAI API key

### 2. Environment Setup

Copy the `.env` file and configure your environment variables:

```bash
# FastAPI
APP_ENV=dev
APP_PORT=8000
JWT_SECRET=your_jwt_secret_here
JWT_EXPIRES_SECONDS=86400

# OpenAI
OPENAI_API_KEY=your_openai_api_key

# AWS S3
AWS_ACCESS_KEY_ID=your_aws_access_key
AWS_SECRET_ACCESS_KEY=your_aws_secret_key
AWS_S3_REGION=us-east-1
AWS_S3_BUCKET=your-bucket-name

# AstraDB
ASTRA_DB_API_ENDPOINT=your_astra_endpoint
ASTRA_DB_APPLICATION_TOKEN=your_astra_token
ASTRA_DB_KEYSPACE=default_keyspace
ASTRA_DB_COLLECTION_USERS=users
ASTRA_DB_COLLECTION_SESSIONS=sessions
ASTRA_DB_COLLECTION_DOCUMENTS=documents
ASTRA_DB_COLLECTION_EMBEDDINGS=embeddings
ASTRA_DB_COLLECTION_MESSAGES=messages
```

### 3. Installation

```bash
# Clone the repository and navigate to project directory
cd rag-chatbot

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 4. Database Setup

Create the following collections in your AstraDB database:

- `users`: User accounts
- `sessions`: Chat sessions
- `documents`: Document metadata
- `embeddings`: Vector embeddings with search index
- `messages`: Conversation history

### 5. Running the Application

```bash
# Development mode
cd app
python main.py

# Or using uvicorn directly
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

The API will be available at `http://localhost:8000` with interactive docs at `http://localhost:8000/docs`.

## API Endpoints

### Authentication
- `POST /auth/register` - User registration
- `POST /auth/login` - User login (returns JWT token)

### Session Management
- `POST /sessions` - Create new chat session
- `GET /sessions` - List user's sessions

### Document Processing
- `POST /documents/upload` - Upload and process PDF (multipart form)

### Chat
- `POST /chat/query` - Query documents with RAG

### Health Check
- `GET /health` - Service health status

## Testing with Postman

### Step 1: Register a User
```http
POST http://localhost:8000/auth/register
Content-Type: application/json

{
  "email": "test@example.com",
  "password": "testpassword123"
}
```

### Step 2: Login
```http
POST http://localhost:8000/auth/login
Content-Type: application/json

{
  "email": "test@example.com",
  "password": "testpassword123"
}
```

Save the `accessToken` from the response for subsequent requests.

### Step 3: Create a Session
```http
POST http://localhost:8000/sessions
Authorization: Bearer <your_access_token>
Content-Type: application/json

{
  "name": "My First Chat"
}
```

Save the `sessionId` from the response.

### Step 4: Upload a PDF
```http
POST http://localhost:8000/documents/upload
Authorization: Bearer <your_access_token>
Content-Type: multipart/form-data

sessionId: <your_session_id>
file: <select_pdf_file>
```

### Step 5: Query the Documents
```http
POST http://localhost:8000/chat/query
Authorization: Bearer <your_access_token>
Content-Type: application/json

{
  "sessionId": "<your_session_id>",
  "message": "What is this document about?"
}
```

## Database Schema

### AstraDB Collections

**users**
```json
{
  "userId": "uuid",
  "email": "string",
  "passwordHash": "string",
  "createdAt": "iso-datetime"
}
```

**sessions**
```json
{
  "sessionId": "uuid",
  "userId": "uuid",
  "name": "string",
  "createdAt": "iso-datetime"
}
```

**documents**
```json
{
  "documentId": "uuid",
  "userId": "uuid",
  "sessionId": "uuid",
  "fileName": "string",
  "s3Key": "string",
  "uploadedAt": "iso-datetime",
  "pages": 123
}
```

**embeddings** (with vector index)
```json
{
  "id": "uuid",
  "content": "string",
  "embedding": [float...],
  "metadata": {
    "userId": "uuid",
    "sessionId": "uuid",
    "documentId": "uuid",
    "source": "pdf_text" | "image_caption",
    "page": 5,
    "fileName": "string"
  }
}
```

**messages**
```json
{
  "messageId": "uuid",
  "userId": "uuid",
  "sessionId": "uuid",
  "role": "user" | "assistant" | "system",
  "content": "string",
  "createdAt": "iso-datetime"
}
```

## Key Features

### Multi-tenant Architecture
- All data is filtered by `userId` extracted from JWT tokens
- Complete isolation between users
- Session-based document access control

### PDF Processing Pipeline
1. **Upload**: PDF uploaded to S3
2. **Text Extraction**: PyMuPDF extracts text per page
3. **Image Extraction**: PyMuPDF extracts embedded images
4. **Image Captioning**: OpenAI GPT-4o-mini generates descriptions
5. **Text Splitting**: LangChain RecursiveCharacterTextSplitter
6. **Embedding**: OpenAI text-embedding-3-small
7. **Storage**: Vectors stored in AstraDB with metadata

### RAG Query Pipeline
1. **Query Embedding**: User question vectorized
2. **Retrieval**: Vector search in AstraDB with user/session filtering
3. **Context Assembly**: Retrieved chunks formatted with source citations
4. **Generation**: OpenAI GPT-4o-mini generates contextual response
5. **History**: Conversation turn saved to database

## Configuration

- **Chunk Size**: 1000 characters
- **Chunk Overlap**: 150 characters
- **Retrieval Top-K**: 5 documents
- **JWT Expiration**: 24 hours (configurable)
- **Max Image Caption**: 200 tokens

## Production Considerations

- Set appropriate CORS origins
- Use strong JWT secrets
- Configure proper AWS IAM roles
- Set up AstraDB production keyspace
- Implement rate limiting
- Add comprehensive logging
- Monitor API usage and costs

## Troubleshooting

- Ensure all environment variables are set
- Verify AstraDB collections exist and have proper indexes
- Check S3 bucket permissions
- Confirm OpenAI API key has sufficient credits
- Test individual components if upload fails

## License

This project is intended for educational/development purposes.