from typing import List, Optional, TypedDict, Any, Dict

from langgraph.graph import StateGraph, END
from langgraph.checkpoint.memory import MemorySaver

from ..schema.models import QueryResponse
from ..services.document_service import DocumentService
from ..services.vector_service import VectorService
from ..services.llm_service import LLMService
from ..tools.text_splitter import DocumentTextSplitter
from ..tools.retriever import DocumentRetriever

class GraphState(TypedDict, total=False):
    file_paths: List[str]
    documents: List[Any]
    chunks: List[Any]
    index_built: bool
    query: str
    max_results: int
    retrieved_documents: List[Any]
    response: QueryResponse


class ResearchGraph:
    """LangGraph workflow for ingestion and query with in-memory checkpointing."""

    def __init__(
        self,
        document_service: DocumentService,
        vector_service: VectorService,
        llm_service: LLMService,
        text_splitter: DocumentTextSplitter,
    ) -> None:
        self.document_service = document_service
        self.vector_service = vector_service
        self.llm_service = llm_service
        self.text_splitter = text_splitter
        self.retriever = DocumentRetriever(vector_service)

        self._ingest_app = self._build_upload_graph()
        self._query_app = self._build_query_graph()

    def _build_upload_graph(self):
        graph = StateGraph(GraphState)

        async def load_and_split(state: GraphState) -> GraphState:
            file_paths = state.get("file_paths", [])
            documents: List[Any] = []
            for path in file_paths:
                docs = await self.document_service._load_pdf_document(path)
                documents.extend(docs)
            if not documents:
                return {"documents": [], "chunks": [], "index_built": False}
            chunks = self.text_splitter.split_documents(documents)
            return {"documents": documents, "chunks": chunks}

        async def build_index(state: GraphState) -> GraphState:
            chunks = state.get("chunks", [])
            success = await self.vector_service.create_vector_store(chunks) if chunks else False
            return {"index_built": bool(success)}

        graph.add_node("load_and_split", load_and_split)
        graph.add_node("build_index", build_index)

        graph.set_entry_point("load_and_split")
        graph.add_edge("load_and_split", "build_index")
        graph.add_edge("build_index", END)

        checkpointer = MemorySaver()
        return graph.compile(checkpointer=checkpointer)

    def _build_query_graph(self):
        graph = StateGraph(GraphState)

        def retrieve(state: GraphState) -> GraphState:
            query = state.get("query", "")
            max_results = state.get("max_results", 5)
            if not query:
                return {"retrieved_documents": []}
            from ..schema.models import QueryRequest

            query_request = QueryRequest(question=query, max_results=max_results, similarity_threshold=0.7)
            docs = self.retriever.retrieve_relevant_documents(query_request)
            return {"retrieved_documents": docs}

        async def generate(state: GraphState) -> GraphState:
            docs = state.get("retrieved_documents", [])
            query = state.get("query", "")
            if not docs:
                return {"response": None}
            response = await self.llm_service.generate_answer(query, docs)
            return {"response": response}

        graph.add_node("retrieve", retrieve)
        graph.add_node("generate", generate)

        graph.set_entry_point("retrieve")
        graph.add_edge("retrieve", "generate")
        graph.add_edge("generate", END)

        checkpointer = MemorySaver()
        return graph.compile(checkpointer=checkpointer)

    async def run_upload(self, uploaded_files: Any, thread_id: Optional[str] = None) -> GraphState:
        temp_paths: List[str] = []
        try:
            for uf in uploaded_files:
                path = await self.document_service._save_temp_file(uf)
                temp_paths.append(path)
            input_state: GraphState = {"file_paths": temp_paths}
            config = {"configurable": {"thread_id": thread_id or "ingest"}}
            result = await self._ingest_app.ainvoke(input_state, config=config)
            return result
        finally:
            for path in temp_paths:
                self.document_service._cleanup_temp_file(path)

    async def run_query(self, query: str, max_results: int = 5, thread_id: Optional[str] = None) -> GraphState:
        input_state: GraphState = {"query": query, "max_results": max_results}
        config = {"configurable": {"thread_id": thread_id or "query"}}
        result = await self._query_app.ainvoke(input_state, config=config)
        return result
