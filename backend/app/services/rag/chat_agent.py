import logging
from typing import Any, Optional, TypedDict

from langgraph.graph import END, StateGraph

from app.helpers.llm.ollama_client import ollama_client
from app.repositories.rag_repository import RagRepository
from app.services.rag.embedding_service import EmbeddingService

logger = logging.getLogger(__name__)


class AgentState(TypedDict):
    messages: list[dict[str, str]]
    query: str
    context: str
    sources: list[dict[str, Any]]
    folder_path: Optional[str]
    final_response: Optional[str]


class RagChatAgent:
    def __init__(
        self,
        repository: RagRepository,
        embedding_service: EmbeddingService,
        model: str = "phi3",
        top_k: int = 5,
    ):
        self.repository = repository
        self.embedding_service = embedding_service
        self.model = model
        self.top_k = top_k
        self.graph = self._build_graph()

    def _build_graph(self) -> StateGraph:
        workflow = StateGraph(AgentState)
        workflow.add_node("retrieve", self._retrieve_node)
        workflow.add_node("augment", self._augment_node)
        workflow.add_node("generate", self._generate_node)
        workflow.set_entry_point("retrieve")
        workflow.add_edge("retrieve", "augment")
        workflow.add_edge("augment", "generate")
        workflow.add_edge("generate", END)
        return workflow.compile()

    async def _retrieve_node(self, state: AgentState) -> dict[str, Any]:
        query = state["query"]
        folder_path = state.get("folder_path")

        logger.info(f"[RETRIEVE] Query: {query[:100]}")

        try:
            query_embedding = await self.embedding_service.embed_text(query)
            results = await self.repository.vector_search(
                embedding=query_embedding,
                folder_path=folder_path,
                limit=self.top_k,
            )

            sources = []
            for row in results:
                sources.append({
                    "document_name": row["file_name"],
                    "chunk_content": row["content"],
                    "relevance_score": row["similarity"],
                    "chunk_id": row["id"],
                    "document_id": row["document_id"],
                })

            logger.info(f"[RETRIEVE] Retrieved {len(sources)} relevant chunks")
            return {"sources": sources}

        except Exception as e:
            logger.error(f"[RETRIEVE] Retrieval failed: {e}", exc_info=True)
            return {"sources": []}

    async def _augment_node(self, state: AgentState) -> dict[str, Any]:
        sources = state["sources"]

        if not sources:
            context = (
                "No relevant documents found in the database. "
                "Please provide a general response or ask for clarification."
            )
            logger.warning("[AUGMENT] No sources available")
        else:
            context_parts = []
            for i, source in enumerate(sources, 1):
                context_parts.append(
                    f"[Document {i}: {source['document_name']}]\n"
                    f"{source['chunk_content']}"
                )
            context = "\n\n---\n\n".join(context_parts)
            logger.info(f"[AUGMENT] Built context from {len(sources)} sources")

        return {"context": context}

    async def _generate_node(self, state: AgentState) -> dict[str, Any]:
        messages = state["messages"]
        context = state["context"]
        query = state["query"]

        system_prompt = """You are a helpful AI assistant that answers questions based on the provided documents.

INSTRUCTIONS:
- Answer based on the provided context when possible
- Be concise but thorough
- If the context doesn't contain relevant information, acknowledge this and provide what help you can
- Reference specific documents when citing information
- If unsure, acknowledge uncertainty rather than making things up"""

        ollama_messages = [{"role": "system", "content": system_prompt}]
        for msg in messages:
            ollama_messages.append({
                "role": msg["role"],
                "content": msg["content"],
            })

        user_prompt = f"""CONTEXT FROM DOCUMENTS:
{context}

USER QUESTION:
{query}"""
        ollama_messages.append({"role": "user", "content": user_prompt})

        logger.info(f"[GENERATE] Sending prompt to LLM (model={self.model})")
        logger.info(f"[GENERATE] Prompt: {user_prompt[:300]}...")

        try:
            response = await ollama_client.chat(
                messages=ollama_messages,
                model=self.model,
                temperature=0.7,
            )

            logger.info(f"[GENERATE] Response generated successfully ({len(response['content'])} chars)")
            return {"final_response": response["content"]}

        except Exception as e:
            logger.error(f"[GENERATE] Generation failed: {e}", exc_info=True)
            return {
                "final_response": (
                    "I apologize, but I encountered an error generating a response. "
                    "Please try again."
                )
            }

    async def chat(
        self,
        query: str,
        conversation_history: Optional[list[dict[str, str]]] = None,
        folder_path: Optional[str] = None,
    ) -> dict[str, Any]:
        state: AgentState = {
            "messages": conversation_history or [],
            "query": query,
            "folder_path": folder_path,
            "context": "",
            "sources": [],
            "final_response": None,
        }

        retrieve_result = await self._retrieve_node(state)
        state.update(retrieve_result)

        augment_result = await self._augment_node(state)
        state.update(augment_result)

        generate_result = await self._generate_node(state)
        state.update(generate_result)

        return {
            "message": state["final_response"],
            "sources": state["sources"],
        }
