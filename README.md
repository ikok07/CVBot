# CVBot Backend

A sophisticated AI-powered personal assistant backend that helps visitors learn about your professional profile through intelligent document retrieval and conversational AI.

## 🚀 Features

- **Intelligent Agent**: LangGraph-powered AI agent that can search through your documents and notify you when information is missing
- **Document Processing**: Advanced OCR and text processing pipeline for various file formats
- **Vector Search**: ChromaDB integration for semantic document search
- **User Management**: Secure authentication and profile management with Clerk
- **API Tracing**: Comprehensive monitoring and debugging with Opik
- **File Management**: CRUD operations for document management in vector database

## 🛠️ Tech Stack

- **Framework**: FastAPI
- **Agent**: LangGraph
- **Database**: PostgreSQL + ChromaDB (vector storage)
- **Authentication**: Clerk
- **OCR**: Docling with EasyOCR
- **Monitoring**: Opik
- **Language**: Python

## 📋 Architecture

### Document Processing Pipeline

1. **File Upload** → PDF files go through Docling OCR extraction
2. **Markdown Conversion** → All content gets converted to markdown format
3. **Smart Chunking** → Text is split by headings, then intelligently chunked by LLM
4. **Context Enhancement** → Each chunk gets contextual information added
5. **Vector Embedding** → Enhanced chunks are embedded and stored in ChromaDB

### Agent Workflow

- **Query Processing** → User questions are processed by LangGraph agent
- **Vector Search** → Agent searches ChromaDB for relevant information
- **Response Generation** → Intelligent responses based on retrieved context
- **Notification System** → Owner gets notified when agent lacks information

## 🔧 API Endpoints

- `/api/v1` - Base endpoint for API V1 endpoints

### File Management
- `POST /vector-store/store-files` - Upload and process documents
- `POST /vector-store/semantic-search` - Search the Vector Store
- `GET /vector-store/retrieve-files` - List all processed files
- `GET /vector-store/retrieve-embeddings?filename=...` - List all embeddings for a file
- `DELETE /vector-store/delete-files` - Remove file from vector database

### Chat
- `POST /chatbot/invoke` - Send message to AI agent
- `GET /chatbot/history?session_id=...` - Retrieve conversation history

## 📊 Monitoring

- The application uses Opik for comprehensive tracing and monitoring

## 🔍 Document Processing Details

### Supported File Formats
- **PDF**: Full OCR processing with Docling
- **Markdown**: Direct processing

### Chunking Strategy (inspired by [Anthropic's Contextual Retrieval](https://www.anthropic.com/news/contextual-retrieval))
1. **Heading-based Split**: Initial split by document structure
2. **LLM-powered Chunking**: Intelligent content-aware chunking
3. **Context Addition**: Each chunk enhanced with surrounding context
4. **Semantic Embedding**: Vector representation for similarity search

## 🤖 Agent Capabilities

The LangGraph agent can:
- Search through your professional documents
- Answer questions about your experience and skills
- Identify knowledge gaps and notify you
- Maintain conversation context
- Provide professional, contextual responses

## 🔐 Security

- **Authentication**: Clerk-based user authentication
- **API Security**: Rate limiting and input validation

## 💻 Installation

1. Go to the `deployment` folder
2. Set the required environment variables in `.env.example` and rename the file to `.env`
3. run `docker compose up`
4. Several docker containers will be started up.
5. NGINX container will expose it's port 80 to the host port 8081 (port can be changed in the `docker-compose.yaml` file)
6. Either use `localhost:8081` or setup a separate reverse proxy pointing to `localhost:8081`
---

#### Originally built by [Kaloyan Stefanov](https://github.com/ikok07)

