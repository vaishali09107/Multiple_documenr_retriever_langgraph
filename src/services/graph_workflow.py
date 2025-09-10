import asyncio
from typing import Any, Dict, List
from langchain.schema import Document
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.graph import END, StateGraph
from ..config.settings import settings
from ..prompts.templates import PromptTemplates
from ..schema.state import ResearchState
from ..services.document_service import DocumentService
from ..services.llm_service import LLMService
from ..services.vector_service import VectorService
from ..tools.text_splitter import DocumentTextSplitter

class ResearchGraph:
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
        self.memory = InMemorySaver()
        self.chat_history: List[Dict[str, str]] = []
        self._active_thread_id: str = "default"

    def _document_to_dict(self, doc: Document) -> Dict[str, Any]:
        return {
            "page_content": doc.page_content,
            "metadata": doc.metadata
        }

    def _dict_to_document(self, doc_dict: Dict[str, Any]) -> Document:
        return Document(
            page_content=doc_dict["page_content"],
            metadata=doc_dict["metadata"]
        )

    def _documents_to_dicts(self, docs: List[Document]) -> List[Dict[str, Any]]:
        return [self._document_to_dict(doc) for doc in docs]

    def _dicts_to_documents(self, doc_dicts: List[Dict[str, Any]]) -> List[Document]:
        return [self._dict_to_document(doc_dict) for doc_dict in doc_dicts]

    def _file_to_dict(self, file) -> Dict[str, Any]:
        return {
            "name": file.name,
            "type": file.type,
            "size": len(file.getvalue()),
            "content": file.getvalue()
        }

    def _dict_to_file(self, file_dict: Dict[str, Any]):
        class FileWrapper:
            def __init__(self, name, type_, content):
                self.name = name
                self.type = type_
                self._content = content
            
            def getvalue(self):
                return self._content
        
        return FileWrapper(
            file_dict["name"],
            file_dict["type"],
            file_dict["content"]
        )

    def _files_to_dicts(self, files: List[Any]) -> List[Dict[str, Any]]:
        return [self._file_to_dict(file) for file in files]

    def _dicts_to_files(self, file_dicts: List[Dict[str, Any]]) -> List[Any]:
        return [self._dict_to_file(file_dict) for file_dict in file_dicts]

    async def run_upload(self, uploaded_files: List[Any], thread_id: str = "default") -> Dict[str, Any]:
        upload_workflow = StateGraph(ResearchState)
        upload_workflow.add_node("validate_files", self._validate_files_node)
        upload_workflow.add_node("process_documents", self._process_documents_node)
        upload_workflow.add_node("create_embeddings", self._create_embeddings_node)
        upload_workflow.add_edge("validate_files", "process_documents")
        upload_workflow.add_edge("process_documents", "create_embeddings")
        upload_workflow.add_edge("create_embeddings", END)
        upload_workflow.set_entry_point("validate_files")

        upload_graph = upload_workflow.compile(checkpointer=self.memory)
        
        initial_state = ResearchState(
            uploaded_files=self._files_to_dicts(uploaded_files),
            processing_status="ingesting"
        )
        config = {"configurable": {"thread_id": thread_id}}
        
        result = await upload_graph.ainvoke(initial_state, config)
        return result

    async def run_query(self, query: str, max_results: int = 5, thread_id: str = "default") -> Dict[str, Any]:
        self._active_thread_id = thread_id
        query_workflow = StateGraph(ResearchState)
        query_workflow.add_node("retrieve_context", self._retrieve_context_node)
        query_workflow.add_node("generate_answer", self._generate_answer_node)
        query_workflow.add_edge("retrieve_context", "generate_answer")
        query_workflow.add_edge("generate_answer", END)
        query_workflow.set_entry_point("retrieve_context")

        query_graph = query_workflow.compile(checkpointer=self.memory)

        query_state = ResearchState(query=query, max_results=max_results)
        config = {"configurable": {"thread_id": thread_id}}

        result = await query_graph.ainvoke(query_state, config)
        
        answer_text = ""
        try:
            if result.get("response") and hasattr(result["response"], "answer"):
                answer_text = result["response"].answer
            elif result.get("response") and isinstance(result["response"], dict):
                answer_text = result["response"].get("answer", "")
        except Exception:
            pass
        
        if query and answer_text:
            self._append_chat_history("user", query)
            self._append_chat_history("assistant", answer_text)
        
        return result

    async def _validate_files_node(self, state: ResearchState) -> Dict[str, Any]:
        valid_files = []
        for file_dict in state.uploaded_files or []:
            try:
                file = self._dict_to_file(file_dict)
                if self.document_service.validate_file(file):
                    valid_files.append(file_dict)
            except Exception:
                continue
        
        if not valid_files:
            return {
                "processing_status": "failed",
                "error": "No valid documents found"
            }
        
        return {
            "uploaded_files": valid_files,
            "processing_status": "validated"
        }

    async def _process_documents_node(self, state: ResearchState) -> Dict[str, Any]:
        if not state.uploaded_files:
            return {
                "processing_status": "failed",
                "error": "No files to process"
            }
        
        async def process_single_file(file_dict):
            try:
                file = self._dict_to_file(file_dict)
                return self.document_service.process_pdf(file)
            except Exception as e:
                print(f"Error processing file {file_dict.get('name', 'unknown')}: {str(e)}")
                return []
        
        tasks = [process_single_file(file_dict) for file_dict in state.uploaded_files]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        all_docs = []
        for result in results:
            if isinstance(result, list):
                all_docs.extend(result)
        
        if not all_docs:
            return {
                "processing_status": "failed",
                "error": "No documents could be processed"
            }
        
        return {
            "processed_documents": self._documents_to_dicts(all_docs),
            "processing_status": "processed"
        }

    async def _create_embeddings_node(self, state: ResearchState) -> Dict[str, Any]:
        if not state.processed_documents:
            return {
                "processing_status": "failed",
                "error": "No documents to embed"
            }
        
        async def split_and_embed_documents(doc_dicts):
            try:
                documents = self._dicts_to_documents(doc_dicts)
                chunks = self.text_splitter.split_documents(documents)
                index_ok = await self.vector_service.create_vector_store_parallel(
                    chunks, 
                    batch_size=settings.EMBEDDING_BATCH_SIZE
                )
                return self._documents_to_dicts(chunks), index_ok
            except Exception as e:
                print(f"Error in split_and_embed_documents: {str(e)}")
                return [], False
        
        chunks, index_ok = await split_and_embed_documents(state.processed_documents)
        
        return {
            "processed_documents": chunks,
            "index_built": bool(index_ok),
            "processing_status": "ready" if index_ok else "failed"
        }

    async def _retrieve_context_node(self, state: ResearchState) -> Dict[str, Any]:
        if not self.vector_service.is_ready():
            return {
                "retrieved_documents": [],
                "processing_status": "no_index",
                "error": "Vector store not initialized"
            }

        docs = await self.vector_service.search_similar_documents_async(
            query=state.query or "",
            k=state.max_results
        )
        return {
            "retrieved_documents": self._documents_to_dicts(docs),
            "processing_status": "retrieved"
        }

    async def _generate_answer_node(self, state: ResearchState) -> Dict[str, Any]:
        retrieved_dicts = state.retrieved_documents or []
        retrieved = self._dicts_to_documents(retrieved_dicts) if retrieved_dicts else []

        if not self.llm_service.is_ready():
            return {
                "response": {
                    "answer": "The language model is not configured.",
                    "confidence_score": None,
                    "processing_time": None,
                    "relevant_chunks": None
                },
                "processing_status": "error"
            }

        if not retrieved:
            return {
                "response": {
                    "answer": "I couldn't find relevant information to answer your question.",
                    "confidence_score": None,
                    "processing_time": None,
                    "relevant_chunks": None
                },
                "processing_status": "answered"
            }

        context = PromptTemplates.format_context(retrieved)
        
        recent_chat_history = self.chat_history[-settings.CHAT_HISTORY_LIMIT:] if len(self.chat_history) > 0 else []
        
        prompt = PromptTemplates.get_research_qa_with_history(
            context=context,
            question=state.query or "",
            chat_history=recent_chat_history
        )

        try:
            llm_response = self.llm_service.llm.invoke(prompt)
            content = getattr(llm_response, "content", None)
            answer_text = content if isinstance(content, str) else str(llm_response)
        except Exception as e:
            answer_text = f"Error generating response: {str(e)}"

        return {
            "response": {
                "answer": answer_text,
                "confidence_score": None,
                "processing_time": None,
                "relevant_chunks": None
            },
            "processing_status": "answered"
        }

    def _append_chat_history(self, role: str, content: str) -> None:
        self.chat_history.append({"role": role, "content": content})
        
    def clear_chat_history(self) -> None:
        self.chat_history.clear()
        
    def get_chat_history(self) -> List[Dict[str, str]]:
        return self.chat_history.copy()

    async def get_conversation_history(self, thread_id: str = "default") -> List[Dict[str, Any]]:
        try:
            config = {"configurable": {"thread_id": thread_id}}
            history = await self.memory.aget_tuple(config)
            if history and history.checkpoint:
                return history.checkpoint.get("channel_values", {})
            return {}
        except Exception as e:
            print(f"Error getting conversation history: {str(e)}")
            return {}

    async def clear_conversation_history(self, thread_id: str = "default") -> None:
        try:
            config = {"configurable": {"thread_id": thread_id}}
            await self.memory.adelete(config)
        except Exception as e:
            print(f"Error clearing conversation history: {str(e)}")