# Document Management Guide

This guide explains how to use the RAG (Retrieval-Augmented Generation) document chat feature.

## Quick Start

### 1. Add Your Documents

Place your documents in the `./documents/` folder in the project root directory:

```bash
./documents/
  ├── my-document.pdf
  ├── company-handbook.docx
  └── api-docs.md
```

**Important:** Only place documents you want to ingest in this folder. Don't add README files or other non-document files.

### 2. Access the RAG Interface

1. Open your browser to http://localhost:5173 (or http://localhost:80 if using nginx)
2. Navigate to the **RAG** tab in the sidebar
3. Click on the **Documents** tab

### 3. Load Documents

In the folder path input, enter:
- `/documents` - the configured documents folder inside the backend container

Click **Load Folder** to see your documents.

### 4. Ingest Documents

Once documents are loaded:
1. Review the list of documents
2. Click **Ingest All** to process them
3. Wait for the ingestion progress bar to complete
4. Documents are now ready for chat!

### 5. Chat with Documents

1. Switch to the **Chat** tab
2. Ask questions about your documents
3. The system will retrieve relevant passages and generate answers

## Supported File Types

| Format | Extension | Notes |
|--------|-----------|-------|
| PDF | `.pdf` | Most common document format |
| Word | `.docx` | Modern Word documents |
| PowerPoint | `.pptx` | Presentation files |
| Excel | `.xlsx` | Spreadsheet files |
| Text | `.txt` | Plain text files |
| Markdown | `.md` | Markdown formatted text |

## How It Works

### Document Ingestion Pipeline

1. **File Reading**: Documents are read from the mounted folder
2. **Text Extraction**: Content is extracted based on file type
3. **Chunking**: Large documents are split into manageable chunks
4. **Embedding**: Each chunk is converted to a 768-dimensional vector using `nomic-embed-text`
5. **Storage**: Chunks and embeddings are stored in PostgreSQL with PGVector

### Chat Pipeline

1. **Query Embedding**: Your question is converted to a vector
2. **Similarity Search**: Relevant chunks are retrieved using cosine similarity
3. **Context Building**: Top matching chunks are used as context
4. **LLM Generation**: Phi3 model generates an answer based on the context
5. **Source Tracking**: References to source documents are provided

## Advanced Usage

### Single Documents Folder

The backend accepts only one documents folder. The folder path you enter must match the configured documents root, and re-ingesting a filename replaces the previous content for that filename.

### Custom Document Location

To use a different folder on your host machine with Docker:

1. Edit `.env` file:
   ```bash
   DOCUMENTS_PATH=/path/to/your/documents
   DOCUMENTS_ROOT=/documents
   ```

2. Restart containers:
   ```bash
   docker compose down
   docker compose up -d
   ```

3. Use path `/documents` in the UI

If you run the backend outside Docker, set `DOCUMENTS_ROOT` to your host path and use that exact path in the UI.

## Troubleshooting

### "Folder not found" Error

**Cause**: The path doesn't exist inside the Docker container.

**Solution**:
- Ensure files are in the `./documents/` folder
- Use path `/documents` (not `./documents`)
- Check that containers are restarted after mounting new volumes

### Documents Not Showing Up

**Cause**: Volume mount not applied or files not in the correct location.

**Solution**:
```bash
# Verify mount inside container
docker exec backend ls -la /documents/

# Recreate container to apply volume mount
docker compose down backend
docker compose up -d backend
```

### Ingestion Fails

**Cause**: Unsupported file type or corrupted file.

**Solution**:
- Check file extension is supported
- Verify file is not corrupted
- Check backend logs: `docker logs backend --tail 50`

### Empty Search Results

**Cause**: Documents not ingested or query mismatch.

**Solution**:
- Verify documents show "completed" status in Documents tab
- Try rephrasing your question
- Ensure folder path is specified in chat

## Performance Tips

1. **Chunk Size**: Default is 1000 characters with 200 character overlap. Good for most documents.

2. **Batch Ingestion**: Ingesting many documents takes time. Process in batches if needed.

3. **Embeddings**: First ingestion generates embeddings (slow). Subsequent chats are fast.

4. **Storage**: Embeddings are stored permanently. Re-ingesting the same filename replaces previous embeddings.

## API Usage

For programmatic access, use the REST API:

### List Documents
```bash
curl "http://localhost:8000/api/v1/rag/documents/folder?folder_path=/documents"
```

### Ingest Documents
```bash
curl -X POST "http://localhost:8000/api/v1/rag/documents/ingest" \
  -H "Content-Type: application/json" \
  -d '{"folder_path": "/documents"}'
```

### Check Status
```bash
curl "http://localhost:8000/api/v1/rag/documents/status?folder_path=/documents"
```

### Chat
```bash
curl -X POST "http://localhost:8000/api/v1/rag/chat" \
  -H "Content-Type: application/json" \
  -d '{"message": "What is RAG?", "folder_path": "/documents"}'
```

## Security Notes

- Documents are mounted **read-only** (`:ro` flag) for security
- The backend cannot modify or delete your source documents
- Embeddings and chunks are stored in PostgreSQL
- No data leaves your local machine (fully local LLM with Ollama)
