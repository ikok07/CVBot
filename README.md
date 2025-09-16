# CVBot Backend

A sophisticated AI-powered personal assistant backend designed to provide seamless access to your professional profile through intelligent document retrieval and conversational AI.

## 🚀 Features

- **Intelligent Agent**: Powered by LangGraph, the AI agent searches through your documents and notifies you when information is missing.
- **Document Processing**: Advanced OCR and text processing pipeline supporting multiple file formats.
- **Vector Search**: ChromaDB integration for efficient semantic document search.
- **API Tracing**: Comprehensive monitoring and debugging with Opik.
- **File Management**: Full CRUD operations for managing documents in a vector database.

## 🛠️ Tech Stack

- **Framework**: FastAPI
- **Agent**: LangGraph
- **Database**: PostgreSQL + ChromaDB (vector storage)
- **Cache/Rate Limiting**: Redis
- **Authentication**: Clerk
- **OCR**: Docling with EasyOCR
- **Monitoring**: Opik
- **Language**: Python

## 📋 Architecture

### Document Processing Pipeline

1. **File Upload**: PDF files are processed via Docling for OCR extraction.
2. **Markdown Conversion**: All content is converted to markdown format for consistency.
3. **Smart Chunking**: Text is split by headings and intelligently chunked using an LLM.
4. **Context Enhancement**: Contextual information is added to each chunk for improved relevance.
5. **Vector Embedding**: Enhanced chunks are embedded and stored in ChromaDB for semantic search.

### Agent Workflow

- **Query Processing**: User queries are handled by the LangGraph agent.
- **Vector Search**: The agent retrieves relevant information from ChromaDB.
- **Response Generation**: Contextual, professional responses are generated based on retrieved data.
- **Notification System**: Alerts the owner when the agent encounters missing information.

## 🛤️ Project Routes

The CVBot Backend is organized into modular routes under the `/api/v1` base endpoint. Below is an overview of the key routes and their functionalities:

- **/vector-store**: Manages document storage and retrieval in the vector database.
  - `POST /vector-store/store-files`: Uploads and processes documents for storage.
  - `POST /vector-store/semantic-search`: Performs semantic search across stored documents.
  - `GET /vector-store/retrieve-files`: Lists all processed files in the vector store.
  - `GET /vector-store/retrieve-embeddings?filename=...`: Retrieves embeddings for a specific file.
  - `DELETE /vector-store/delete-files`: Removes specified files from the vector database.
- **/projects**: Handles project-related operations for managing your portfolio.
  - `GET /projects`: Retrieves a list of all projects.
  - `POST /projects`: Adds a new project to the database.
  - `DELETE /projects/{project_id}`: Deletes a project by its ID.
- **/chatbot**: Facilitates interaction with the AI-powered chatbot.
  - `POST /chatbot/invoke`: Sends a user message to the AI agent for processing. **Rate limited to 20 requests per minute per user** to ensure fair usage and prevent abuse.
  - `GET /chatbot/history?session_id=...`: Retrieves the conversation history for a given session.

---
**`vector-store` and `projects` routes are secured with Clerk authentication.**

---

## 📊 Monitoring

- Comprehensive tracing and monitoring are enabled through Opik, ensuring reliable performance and debugging capabilities.

## 🔍 Document Processing Details

### Supported File Formats
- **PDF**: Processed with Docling for full OCR support.
- **Markdown**: Directly processed for efficient handling.

### Chunking Strategy (Inspired by [Anthropic's Contextual Retrieval](https://www.anthropic.com/news/contextual-retrieval))
1. **Heading-based Split**: Documents are split based on their structural headings.
2. **LLM-powered Chunking**: Content is intelligently chunked for optimal processing.
3. **Context Addition**: Chunks are enhanced with surrounding context for better search accuracy.
4. **Semantic Embedding**: Chunks are converted into vector representations for similarity search.

## 🤖 Agent Capabilities

The LangGraph-powered agent offers:
- Semantic search through professional documents.
- Contextual answers about your experience and skills.
- Identification of knowledge gaps with owner notifications.
- Conversation context maintenance for seamless interactions.
- Professional, tailored responses based on retrieved data.

## 🔐 Security

- **Authentication**: Clerk-based user authentication for secure access.
- **API Security**: Rate limiting (e.g., 20 requests per minute for `/chatbot/invoke`, stored in Redis) and robust input validation to prevent abuse.

## 💻 Installation

1. Navigate to the `deployment` folder.
2. Copy `.env.example` to `.env` and configure the required environment variables, including Redis connection settings.
3. Run `docker compose up` to start the application, including the Redis container.
4. Docker containers will initialize, with the NGINX container exposing port 80 to the host's port 8081 (configurable in `docker-compose.yaml`).
5. Access the application via `localhost:8081` or set up a reverse proxy pointing to `localhost:8081`.

## 👨‍💻 Author

Originally built by [Kaloyan Stefanov](https://github.com/ikok07).