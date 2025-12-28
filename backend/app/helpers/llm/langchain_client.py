"""
LangChain client for complex LLM workflows.

Features:
- Chain composition
- Vector store integration (PGVector)
- Document loaders
- Agents and tools
- Memory management
- RAG (Retrieval Augmented Generation)
"""

from typing import Any, Dict, List, Optional

try:
    from langchain.chains import ConversationalRetrievalChain, LLMChain
    from langchain.memory import ConversationBufferMemory
    from langchain.prompts import PromptTemplate
    from langchain_community.vectorstores import PGVector
    from langchain_openai import ChatOpenAI, OpenAIEmbeddings
    LANGCHAIN_AVAILABLE = True
except ImportError:
    LANGCHAIN_AVAILABLE = False

from app.config.settings import settings


class LangChainClient:
    """LangChain integration for complex LLM workflows."""

    def __init__(self):
        self.enabled = settings.enable_llm_langchain and LANGCHAIN_AVAILABLE
        self._llm = None
        self._embeddings = None
        self._vectorstore = None

    def _get_llm(self, model: str = "gpt-3.5-turbo", temperature: float = 0.7):
        """Get or create LLM instance."""
        if not self.enabled:
            raise RuntimeError("LangChain is not enabled or not installed")

        if not settings.enable_llm_openai or not settings.openai_api_key:
            raise RuntimeError("OpenAI API key is required for LangChain")

        return ChatOpenAI(
            model=model,
            temperature=temperature,
            openai_api_key=settings.openai_api_key,
        )

    def _get_embeddings(self):
        """Get or create embeddings instance."""
        if not self.enabled:
            raise RuntimeError("LangChain is not enabled or not installed")

        if self._embeddings is None:
            self._embeddings = OpenAIEmbeddings(
                openai_api_key=settings.openai_api_key
            )
        return self._embeddings

    def get_vectorstore(self, collection_name: str = "documents"):
        """
        Get PGVector vectorstore for document retrieval.

        Args:
            collection_name: Name of the vector collection

        Returns:
            PGVector instance
        """
        if not self.enabled:
            raise RuntimeError("LangChain is not enabled or not installed")

        if not settings.enable_postgres or not settings.enable_pgvector:
            raise RuntimeError("PostgreSQL with PGVector is required")

        connection_string = settings.database_url.replace(
            "postgresql+asyncpg://", "postgresql://"
        )

        return PGVector(
            collection_name=collection_name,
            connection_string=connection_string,
            embedding_function=self._get_embeddings(),
        )

    async def simple_completion(
        self,
        prompt: str,
        model: str = "gpt-3.5-turbo",
        temperature: float = 0.7,
    ) -> str:
        """
        Simple completion with prompt template.

        Args:
            prompt: Input prompt
            model: Model identifier
            temperature: Sampling temperature

        Returns:
            Completion text
        """
        llm = self._get_llm(model=model, temperature=temperature)
        return await llm.ainvoke(prompt)

    async def chain_completion(
        self,
        template: str,
        input_variables: Dict[str, Any],
        model: str = "gpt-3.5-turbo",
    ) -> str:
        """
        Run completion with prompt template and variables.

        Args:
            template: Prompt template with {variables}
            input_variables: Dict of variable values
            model: Model identifier

        Returns:
            Completion text
        """
        if not self.enabled:
            raise RuntimeError("LangChain is not enabled or not installed")

        llm = self._get_llm(model=model)
        prompt = PromptTemplate(
            template=template,
            input_variables=list(input_variables.keys()),
        )
        chain = LLMChain(llm=llm, prompt=prompt)
        result = await chain.ainvoke(input_variables)
        return result["text"]

    async def rag_query(
        self,
        query: str,
        collection_name: str = "documents",
        model: str = "gpt-3.5-turbo",
        k: int = 4,
    ) -> Dict[str, Any]:
        """
        Retrieval Augmented Generation query.

        Args:
            query: User question
            collection_name: Vector collection to search
            model: LLM model identifier
            k: Number of documents to retrieve

        Returns:
            Dict with answer and source documents
        """
        if not self.enabled:
            raise RuntimeError("LangChain is not enabled or not installed")

        vectorstore = self.get_vectorstore(collection_name)
        llm = self._get_llm(model=model)

        memory = ConversationBufferMemory(
            memory_key="chat_history",
            return_messages=True,
        )

        qa_chain = ConversationalRetrievalChain.from_llm(
            llm=llm,
            retriever=vectorstore.as_retriever(search_kwargs={"k": k}),
            memory=memory,
            return_source_documents=True,
        )

        result = await qa_chain.ainvoke({"question": query})

        return {
            "answer": result["answer"],
            "sources": [
                {
                    "content": doc.page_content,
                    "metadata": doc.metadata,
                }
                for doc in result["source_documents"]
            ],
        }

    async def add_documents(
        self,
        texts: List[str],
        metadatas: Optional[List[Dict[str, Any]]] = None,
        collection_name: str = "documents",
    ) -> List[str]:
        """
        Add documents to vector store.

        Args:
            texts: List of document texts
            metadatas: Optional metadata for each document
            collection_name: Vector collection name

        Returns:
            List of document IDs
        """
        if not self.enabled:
            raise RuntimeError("LangChain is not enabled or not installed")

        vectorstore = self.get_vectorstore(collection_name)
        return await vectorstore.aadd_texts(texts=texts, metadatas=metadatas)

    async def similarity_search(
        self,
        query: str,
        collection_name: str = "documents",
        k: int = 4,
    ) -> List[Dict[str, Any]]:
        """
        Search for similar documents.

        Args:
            query: Search query
            collection_name: Vector collection
            k: Number of results

        Returns:
            List of similar documents with scores
        """
        if not self.enabled:
            raise RuntimeError("LangChain is not enabled or not installed")

        vectorstore = self.get_vectorstore(collection_name)
        results = await vectorstore.asimilarity_search_with_score(query, k=k)

        return [
            {
                "content": doc.page_content,
                "metadata": doc.metadata,
                "score": score,
            }
            for doc, score in results
        ]


# Global instance
langchain_client = LangChainClient()
