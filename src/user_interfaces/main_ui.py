import streamlit as st
import asyncio
from .components.document_uploader import DocumentUploader
from .components.query_interface import QueryInterface
from .components.results_display import ResultsDisplay
from ..services.document_service import DocumentService
from ..services.vector_service import VectorService
from ..services.llm_service import LLMService
from ..tools.text_splitter import DocumentTextSplitter
from ..tools.retriever import DocumentRetriever
from ..services.graph_workflow import ResearchGraph
from ..config.settings import settings
from ..schema.models import AppState, QueryRequest
from ..user_interfaces.Styles.styles import apply_custom_styles

def main():
    """Main Streamlit application"""
    
    st.set_page_config(
        page_title="Multi-Document Research Assistant",
        page_icon="📚",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    apply_custom_styles()
    
    _initialize_session_state()
    
    _render_sidebar()
    
    _render_main_content()


def _initialize_session_state():
    """Initialize Streamlit session state"""
    
    if 'document_service' not in st.session_state:
        st.session_state.document_service = DocumentService()
    
    if 'vector_service' not in st.session_state:
        st.session_state.vector_service = VectorService()
    
    if 'llm_service' not in st.session_state:
        try:
            st.session_state.llm_service = LLMService()
        except Exception as e:
            st.error(f"Failed to initialize LLM service: {str(e)}")
            st.stop()
    
    if 'text_splitter' not in st.session_state:
        st.session_state.text_splitter = DocumentTextSplitter()
    
    if 'retriever' not in st.session_state:
        st.session_state.retriever = DocumentRetriever(st.session_state.vector_service)
    
    if 'document_uploader' not in st.session_state:
        st.session_state.document_uploader = DocumentUploader()
    
    if 'query_interface' not in st.session_state:
        st.session_state.query_interface = QueryInterface()
    
    if 'results_display' not in st.session_state:
        st.session_state.results_display = ResultsDisplay()
    
    if 'app_state' not in st.session_state:
        st.session_state.app_state = AppState()

    if 'graph' not in st.session_state:
        st.session_state.graph = ResearchGraph(
            document_service=st.session_state.document_service,
            vector_service=st.session_state.vector_service,
            llm_service=st.session_state.llm_service,
            text_splitter=st.session_state.text_splitter,
        )

def _render_sidebar():
    """Render simple sidebar with status"""
    
    with st.sidebar:
        st.markdown("Research Assistant")
        st.markdown("---")
        
        st.markdown("Status")
        
        if st.session_state.app_state.vector_store_ready:
            stats = st.session_state.vector_service.get_stats()
            st.markdown(f"**Documents:** {stats.total_documents}")
            st.markdown(f"**Text Chunks:** {stats.total_chunks}")
        else:
            st.info("No documents loaded")
        
        st.markdown("---")
        
        if st.button("Clear Data", type="secondary"):
            if st.session_state.vector_service.is_ready():
                st.session_state.vector_service.clear_vector_store()
                st.session_state.app_state = AppState()
                st.rerun()

def _render_main_content():
    """Render main content area"""
    
    st.markdown('<h1 class="main-header">Multi-Document Research Assistant</h1>', unsafe_allow_html=True)
    st.markdown('<p class="sub-header">Upload documents and ask questions across multiple sources</p>', unsafe_allow_html=True)
    
    tab1, tab2 = st.tabs(["Upload Documents", "Ask Questions"])
    
    with tab1:
        _render_upload_tab()
    
    with tab2:
        _render_query_tab()

def _render_upload_tab():
    """Render document upload tab"""
    
    st.markdown("Upload Your Documents")
    
    uploaded_files = st.session_state.document_uploader.render()
    
    if uploaded_files:
        with st.spinner("Processing documents..."):
            success = asyncio.run(_process_uploaded_documents(uploaded_files))
            
            if success:
                st.success(f"Successfully processed {len(uploaded_files)} documents!")
                st.session_state.app_state.documents_loaded = True
                st.session_state.app_state.vector_store_ready = True
                st.rerun()
            else:
                st.error("Failed to process some documents. Please try again.")

def _render_query_tab():
    """Render query interface tab"""
    
    if not st.session_state.app_state.vector_store_ready:
        st.warning("Please upload some documents first before asking questions.")
        return
    
    st.markdown("Ask Your Questions")
    
    query_data = st.session_state.query_interface.render()
    
    if query_data:
        query_request = QueryRequest(
            question=query_data['question'],
            max_results=query_data.get('max_results', 5),
            similarity_threshold=0.7
        )
        
        with st.spinner("Searching and generating answer..."):
            response = asyncio.run(_process_query(query_request))
            
            if response:
                st.session_state.results_display.render(response)
            else:
                st.error("No answer generated. Please try a different question or check if documents are properly loaded.")

async def _process_uploaded_documents(uploaded_files) -> bool:
    """Process uploaded documents"""
    try:
        state = await st.session_state.graph.run_upload(uploaded_files, thread_id="ui_ingest")
        success = bool(state.get('index_built'))
        return success
        
    except Exception as e:
        st.error(f"Error processing documents: {str(e)}")
        return False

async def _process_query(query_request: QueryRequest):
    """Process user query"""
    try:
        state = await st.session_state.graph.run_query(
            query=query_request.question,
            max_results=query_request.max_results,
            thread_id="ui_query",
        )
        return state.get('response')
        
    except Exception as e:
        st.error(f"Error processing query: {str(e)}")
        return None

if __name__ == "__main__":
    main()