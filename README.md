# Mini RAG App

**Status: Work in Progress**  
**Latest branch: `tut-007`**

Mini RAG App is a Retrieval-Augmented Generation (RAG) backend being built incrementally. The current implementation focuses on the document-ingestion foundation: project management, file uploads, document parsing, text chunking, MongoDB persistence, and the initial abstraction for LLM providers.

> This repository is still under development. The complete retrieval and question-answering workflow is not implemented yet.

## Current implementation

### 1. API foundation
- FastAPI application with versioned routes under `/api/v1`.
- Startup and shutdown lifecycle hooks.
- Application-level initialization of MongoDB and LLM provider clients.

### 2. Document upload and validation
- Upload endpoint: `POST /api/v1/data/upload/{project_id}`.
- Supports plain-text (`.txt`) and PDF documents.
- Validates uploaded content type and configured file-size limit.
- Generates unique file names and stores uploaded files under a project-specific directory.
- Saves file metadata in MongoDB.

### 3. Document processing and chunking
- Processing endpoint: `POST /api/v1/data/process/{project_id}`.
- Loads text files with LangChain's `TextLoader` and PDFs with `PyMuPDFLoader`.
- Splits document content with `RecursiveCharacterTextSplitter`.
- Supports configurable chunk size, overlap, processing a selected file, and resetting existing project chunks.
- Stores chunk text, metadata, order, project ID, and asset ID in MongoDB.

### 4. MongoDB data layer
The current data models cover:
- **Projects** — project identifiers.
- **Assets** — uploaded-file metadata.
- **Chunks** — processed text chunks and their metadata.

MongoDB is configured through Docker Compose. The application uses Motor for asynchronous MongoDB access and defines indexes for project, asset, and chunk collections.

### 5. LLM provider foundation
The code introduces a provider abstraction and factory for:
- OpenAI
- Cohere

The provider classes define interfaces for configuring embedding and generation models, generating text, creating embeddings, and constructing prompts. These integrations are currently part of the in-progress implementation and should not yet be considered a completed end-to-end RAG pipeline.

## Technology stack

- **Language:** Python
- **API:** FastAPI, Uvicorn
- **Database:** MongoDB, Motor
- **Document processing:** LangChain document loaders and `RecursiveCharacterTextSplitter`, PyMuPDF
- **LLM providers:** OpenAI, Cohere
- **Validation/configuration:** Pydantic, pydantic-settings
- **Infrastructure:** Docker, Docker Compose

## Project structure

```text
mini-RAG-app/
├── docker/
│   └── docker-compose.yml
├── src/
│   ├── controllers/
│   │   ├── BaseController.py
│   │   ├── DataController.py
│   │   ├── ProcessController.py
│   │   └── ProjectController.py
│   ├── helper/
│   │   └── config.py
│   ├── models/
│   │   ├── db_schemes/
│   │   ├── enums/
│   │   ├── AssetModel.py
│   │   ├── ChunkModel.py
│   │   └── ProjectModel.py
│   ├── routes/
│   │   ├── schemas/
│   │   ├── base.py
│   │   └── data.py
│   ├── stores/
│   │   └── llm/
│   │       ├── providers/
│   │       ├── LLMEnums.py
│   │       ├── LLMFactory.py
│   │       └── LLMInterface.py
│   ├── assets/
│   ├── main.py
│   └── requirements.txt
└── README.md
```

## API endpoints currently present

| Method | Endpoint | Purpose |
|---|---|---|
| `GET` | `/api/v1/` | Basic API information |
| `POST` | `/api/v1/data/upload/{project_id}` | Upload a TXT or PDF file to a project |
| `POST` | `/api/v1/data/process/{project_id}` | Parse uploaded files, split them into chunks, and save the chunks |

The processing request accepts:
- `file_id` (optional): process one previously uploaded file; if omitted, process all project files.
- `chunk_size` (optional): text chunk size; current schema default is `100`.
- `overlap_size` (optional): overlap between chunks; current schema default is `20`.
- `do_reset` (optional): set to `1` to delete the project's existing chunks before processing.

## Setup

The following describes the intended local setup. Because the project is under active development, configuration and provider integration may require fixes before the application starts successfully.

### 1. Clone the repository and select the current branch

```bash
git clone https://github.com/Shahdali812004/Mini-RAG-App.git
cd Mini-RAG-App
git checkout tut-007
```

### 2. Create and activate a Python environment

```bash
conda create -n mini-rag python=3.10
conda activate mini-rag
```

### 3. Install dependencies

```bash
cd src
pip install -r requirements.txt
```

The current source imports `langchain_community` document loaders. Ensure the matching `langchain-community` package is installed; it is not currently listed explicitly in `src/requirements.txt`.

### 4. Configure environment variables

Create local environment files from the examples:

```bash
cp .env.example .env
cd ../docker
cp .env.example .env
```

Fill in the MongoDB credentials and connection settings, plus the API credentials and model settings for the providers you intend to use. Keep real credentials in local `.env` files only; never commit them.

The settings names in `src/helper/config.py` and `src/.env.example` are not fully aligned in the current snapshot. Review the names before running the application. In particular, the settings model expects `FILE_ALLOWED_TYPES` and `FILE_ALLOWED_SIZE_MB`.

### 5. Start MongoDB

From the `docker` directory:

```bash
docker compose up -d
```

### 6. Start the API

From the `src` directory:

```bash
uvicorn main:app --reload --host 0.0.0.0 --port 5000
```

When startup configuration is valid, the API documentation is available at:

```text
http://localhost:5000/docs
```

## Example workflow

1. Start MongoDB.
2. Start the FastAPI application.
3. Create or identify a project ID.
4. Upload a `.txt` or `.pdf` file using `POST /api/v1/data/upload/{project_id}`.
5. Process the uploaded file using `POST /api/v1/data/process/{project_id}`.
6. Inspect the response for the number of processed files and inserted chunks.

A Postman collection is included at `src/assets/mini-rag-app.postman_collection.json`.

## Planned work

The following are natural next stages for completing the RAG workflow; they are not claimed as implemented in the current snapshot:

- Generate and persist embeddings for document chunks.
- Add vector similarity search and retrieval.
- Build a question-answering endpoint that retrieves relevant context.
- Connect retrieved context to an LLM generation flow.
- Add retrieval and answer-quality evaluation.
- Improve error handling, configuration validation, and automated tests.

## Development note

This project is being developed incrementally as a hands-on learning project. Features and setup instructions will be updated and the implementation evolves.
