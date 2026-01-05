#!/bin/bash
set -e

GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m'

API_URL="http://localhost:8000/api/v1"
HOST_DOCUMENTS_PATH="${DOCUMENTS_PATH:-${DOCUMENTS_ROOT:-./documents}}"
API_DOCUMENTS_PATH="${DOCUMENTS_ROOT:-/documents}"

echo -e "${YELLOW}🧪 Testing RAG Workflow...${NC}\n"

# 1. Check health endpoint
echo -e "${YELLOW}1. Checking service health...${NC}"
HEALTH=$(curl -s http://localhost:8000/health | jq -r '.status')
if [ "$HEALTH" = "healthy" ]; then
    echo -e "${GREEN}✓ Backend is healthy${NC}"
else
    echo -e "${RED}✗ Backend health check failed${NC}"
    exit 1
fi

# 2. Check if test documents exist
echo -e "\n${YELLOW}2. Checking test documents...${NC}"
FOLDER_EXISTS=$(curl -s "${API_URL}/rag/documents/folder?folder_path=${API_DOCUMENTS_PATH}" | jq -r '.total_count // 0')
if [ "$FOLDER_EXISTS" -gt 0 ]; then
    echo -e "${GREEN}✓ Found ${FOLDER_EXISTS} documents in test folder${NC}"
else
    echo -e "${YELLOW}⚠ No documents found. Creating test documents...${NC}"
    mkdir -p "$HOST_DOCUMENTS_PATH"

    cat > "${HOST_DOCUMENTS_PATH}/rag-intro.txt" << 'EOF'
# Introduction to RAG

RAG (Retrieval-Augmented Generation) is a powerful technique that combines information retrieval with large language models. It allows AI systems to access external knowledge bases and use that information to generate more accurate and contextual responses.

Key components of RAG:
1. Document Retrieval: Finding relevant documents from a knowledge base
2. Augmentation: Adding retrieved context to the prompt
3. Generation: Using an LLM to generate responses based on the augmented context

RAG is particularly useful for:
- Question answering systems
- Chatbots with domain-specific knowledge
- Knowledge management applications
EOF

    cat > "${HOST_DOCUMENTS_PATH}/embeddings.txt" << 'EOF'
# Vector Embeddings

Vector embeddings are numerical representations of text that capture semantic meaning. In RAG systems, documents and queries are converted into embeddings for similarity search.

The nomic-embed-text model generates 768-dimensional embeddings that are particularly effective for semantic search tasks. These embeddings allow RAG systems to find relevant documents even when the exact keywords do not match.

Common embedding models:
- nomic-embed-text: 768 dimensions, open source
- OpenAI text-embedding-ada-002: 1536 dimensions
- sentence-transformers: Various sizes
EOF

    echo -e "${GREEN}✓ Created test documents${NC}"
fi

# 3. Check document status
echo -e "\n${YELLOW}3. Checking document ingestion status...${NC}"
INGESTED=$(curl -s "${API_URL}/rag/documents/status?folder_path=${API_DOCUMENTS_PATH}" | jq 'map(select(.status == "completed")) | length')
if [ "$INGESTED" -gt 0 ]; then
    echo -e "${GREEN}✓ ${INGESTED} documents already ingested${NC}"
else
    echo -e "${YELLOW}⚠ No documents ingested. Run ingestion manually via UI or API${NC}"
fi

# 4. Test chat endpoint
echo -e "\n${YELLOW}4. Testing RAG chat functionality...${NC}"
CHAT_RESPONSE=$(curl -s -X POST "${API_URL}/rag/chat" \
    -H 'Content-Type: application/json' \
    -d "{\"message\": \"What is RAG?\", \"folder_path\": \"${API_DOCUMENTS_PATH}\"}")

CONVERSATION_ID=$(echo "$CHAT_RESPONSE" | jq -r '.conversation_id // empty')
MESSAGE=$(echo "$CHAT_RESPONSE" | jq -r '.message // empty')
SOURCE_COUNT=$(echo "$CHAT_RESPONSE" | jq '.sources | length // 0')

if [ -n "$CONVERSATION_ID" ] && [ -n "$MESSAGE" ]; then
    echo -e "${GREEN}✓ Chat endpoint working${NC}"
    echo -e "  Conversation ID: ${CONVERSATION_ID}"
    echo -e "  Sources retrieved: ${SOURCE_COUNT}"
    echo -e "  Response preview: ${MESSAGE:0:100}..."
else
    echo -e "${RED}✗ Chat endpoint failed${NC}"
    echo "Response: $CHAT_RESPONSE"
    exit 1
fi

# 5. Test conversation listing
echo -e "\n${YELLOW}5. Testing conversation history...${NC}"
CONVERSATIONS=$(curl -s "${API_URL}/rag/conversations?limit=5" | jq 'length')
if [ "$CONVERSATIONS" -ge 0 ]; then
    echo -e "${GREEN}✓ Found ${CONVERSATIONS} conversations${NC}"
else
    echo -e "${RED}✗ Conversation listing failed${NC}"
    exit 1
fi

# 6. Test frontend accessibility
echo -e "\n${YELLOW}6. Testing frontend accessibility...${NC}"
FRONTEND_STATUS=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:5173)
if [ "$FRONTEND_STATUS" = "200" ]; then
    echo -e "${GREEN}✓ Frontend is accessible${NC}"
else
    echo -e "${YELLOW}⚠ Frontend returned status ${FRONTEND_STATUS}${NC}"
fi

# 7. Test Ollama availability
echo -e "\n${YELLOW}7. Testing Ollama service...${NC}"
OLLAMA_STATUS=$(curl -s http://localhost:11434/api/tags | jq -r '.models | length // 0')
if [ "$OLLAMA_STATUS" -gt 0 ]; then
    echo -e "${GREEN}✓ Ollama is running with ${OLLAMA_STATUS} models${NC}"
else
    echo -e "${YELLOW}⚠ Ollama may not be fully ready${NC}"
fi

echo -e "\n${GREEN}🎉 RAG Workflow Test Complete!${NC}"
echo -e "\n${YELLOW}Next steps:${NC}"
echo -e "  • Open http://localhost:5173 to access the UI"
echo -e "  • Navigate to the RAG tab to test document ingestion and chat"
echo -e "  • API documentation: http://localhost:8000/docs"
