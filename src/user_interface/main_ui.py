import asyncio
import streamlit as st
from ..config.settings import settings
from ..services.document_service import DocumentService
from ..services.graph_workflow import ResearchGraph
from ..services.llm_service import LLMService
from ..services.vector_service import VectorService
from ..tools.text_splitter import DocumentTextSplitter
from .components.document_uploader import DocumentUploader
from .components.query_interface import QueryInterface
from .components.results_display import ResultsDisplay

def main():
    st.set_page_config(
        page_title="Multi-Document Research Assistant",
        page_icon="📚",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    _initialize_session_state()
    _render_sidebar()
    _render_main_content()

def _initialize_session_state():
    if 'document_service' not in st.session_state:
        st.session_state.document_service = DocumentService()
    
    if 'vector_service' not in st.session_state:
        st.session_state.vector_service = VectorService()
    
    if 'llm_service' not in st.session_state:
        st.session_state.llm_service = LLMService()
    
    if 'text_splitter' not in st.session_state:
        st.session_state.text_splitter = DocumentTextSplitter()
    
    if 'document_uploader' not in st.session_state:
        st.session_state.document_uploader = DocumentUploader()
    
    if 'query_interface' not in st.session_state:
        st.session_state.query_interface = QueryInterface()
    
    if 'results_display' not in st.session_state:
        st.session_state.results_display = ResultsDisplay()
    
    if 'chat_history' not in st.session_state:
        st.session_state.chat_history = []
    
    if 'graph' not in st.session_state:
        st.session_state.graph = ResearchGraph(
            document_service=st.session_state.document_service,
            vector_service=st.session_state.vector_service,
            llm_service=st.session_state.llm_service,
            text_splitter=st.session_state.text_splitter,
        )
        st.session_state.graph.chat_history = st.session_state.chat_history
    
    if 'documents_loaded' not in st.session_state:
        st.session_state.documents_loaded = False
    
    if 'vector_store_ready' not in st.session_state:
        st.session_state.vector_store_ready = False

def _render_sidebar():
    with st.sidebar:
        st.markdown("### Research Assistant")
        st.markdown("---")
        
        st.markdown("**Status**")
        
        if st.session_state.vector_store_ready:
            st.success("Documents loaded and ready")
        else:
            st.info("No documents loaded")
        
        st.markdown("---")
        
        if st.button("Clear Data", type="secondary"):
            if st.session_state.vector_service.is_ready():
                st.session_state.vector_service.vector_store = None
                st.session_state.documents_loaded = False
                st.session_state.vector_store_ready = False
                st.rerun()
        
        st.markdown("---")
        
        if st.button("Clear Chat History", type="secondary"):
            st.session_state.chat_history.clear()
            st.session_state.graph.chat_history = st.session_state.chat_history
            st.success("Chat history cleared!")
            st.rerun()

def _render_main_content():
    st.title("Multi-Document Research Assistant")
    st.markdown("Upload documents and ask questions across multiple sources")
    
    tab1, tab2, tab3 = st.tabs(["📄 Upload Documents", "❓ Ask Questions", "💬 Chat History"])
    
    with tab1:
        _render_upload_tab()
    
    with tab2:
        _render_query_tab()
    
    with tab3:
        _render_chat_history_tab()

def _render_upload_tab():
    st.header("Upload Your Documents")
    
    uploaded_files = st.session_state.document_uploader.render()
    
    if uploaded_files:
        with st.spinner("Processing documents..."):
            success = asyncio.run(_process_uploaded_documents(uploaded_files))
            
            if success:
                st.success(f"Successfully processed {len(uploaded_files)} documents!")
                st.session_state.documents_loaded = True
                st.session_state.vector_store_ready = True
                st.rerun()
            else:
                st.error("Failed to process documents. Please try again.")

def _render_query_tab():
    if not st.session_state.vector_store_ready:
        st.warning("Please upload documents first before asking questions.")
        return
    
    st.header("Ask Your Questions")
    
    if st.session_state.chat_history:
        with st.expander("Recent Chat History", expanded=False):
            recent_history = st.session_state.chat_history[-settings.UI_CHAT_HISTORY_DISPLAY:]
            for i, message in enumerate(recent_history):
                role = message.get("role", "user")
                content = message.get("content", "")
                if role == "user":
                    st.markdown(f"**You:** {content}")
                else:
                    st.markdown(f"**Assistant:** {content}")
                if i < len(recent_history) - 1:
                    st.markdown("---")
    
    query_data = st.session_state.query_interface.render()
    
    if query_data:
        with st.spinner("Searching and generating answer..."):
            response = asyncio.run(_process_query(query_data))
            
            if response:
                st.session_state.results_display.render(response)
            else:
                st.error("No answer generated. Please try a different question.")

def _render_chat_history_tab():
    st.header("Complete Chat History")
    
    if not st.session_state.chat_history:
        st.info("No chat history available. Start asking questions to see the conversation here.")
        return
    
    for i, message in enumerate(st.session_state.chat_history):
        role = message.get("role", "user")
        content = message.get("content", "")
        
        if role == "user":
            with st.chat_message("user"):
                st.write(content)
        else:
            with st.chat_message("assistant"):
                st.write(content)
        
        if i < len(st.session_state.chat_history) - 1:
            st.markdown("---")

async def _process_uploaded_documents(uploaded_files) -> bool:
    try:
        state = await st.session_state.graph.run_upload(uploaded_files, thread_id="ui_ingest")
        return bool(state.get('index_built'))
    except Exception as e:
        st.error(f"Error processing documents: {str(e)}")
        return False

async def _process_query(query_data):
    try:
        state = await st.session_state.graph.run_query(
            query=query_data['question'],
            max_results=query_data.get('max_results', 5),
            thread_id="ui_query",
        )
        st.session_state.chat_history = st.session_state.graph.chat_history
        return state.get('response')
    except Exception as e:
        st.error(f"Error processing query: {str(e)}")
        return None

if __name__ == "__main__":
    main()