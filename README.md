# Multi-Document Research Assistant

A LangGraph-powered research assistant that processes multiple PDF documents and answers queries across all sources using vector similarity search and advanced language models.

## Features

- **LangGraph Integration**: Complete workflow with graph nodes, state management, and persistent memory
- **Multi-Document Processing**: Upload and process multiple PDF documents simultaneously
- **Vector Search**: FAISS-powered similarity search for relevant content retrieval
- **Advanced LLM**: Gemini 2.0 Flash for comprehensive answer generation
- **Interactive UI**: Clean Streamlit interface with real-time processing
- **Contextual Memory**: Maintains conversation context across sessions
- **Human-in-the-Loop**: Interactive approval points for document processing

## Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd multi_document_research_assistant
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Set up environment variables:
```bash
# Create .env file
echo "GOOGLE_API_KEY=your_gemini_api_key_here" > .env
```

4. Run the application:
```bash
streamlit run app.py
```

## Usage

1. **Upload Documents**: Use the "Upload Documents" tab to upload PDF files
2. **Ask Questions**: Switch to "Ask Questions" tab and enter your queries
3. **Review Answers**: Get comprehensive answers with source references

## Project Structure

```
src/
├── agents/          # LangGraph agents and workflows
├── schema/          # Pydantic state models and schemas
├── config/          # Application settings and configuration
├── tools/           # Document processing and text splitting tools
├── utils/           # Validation and utility functions
├── services/        # Core services (vector store, LLM, embeddings)
└── user_interface/  # Streamlit UI components
```

## Configuration

Key settings in `src/config/settings.py`:

- `MODEL_NAME`: Gemini model (default: gemini-2.0-flash-exp)
- `EMBEDDING_MODEL`: HuggingFace embedding model
- `CHUNK_SIZE`: Text chunk size for processing
- `CHUNK_OVERLAP`: Overlap between text chunks
- `MAX_UPLOAD_SIZE`: Maximum file size limit

## LangGraph Components

- **Graph Workflow**: Document processing and query handling pipeline
- **State Management**: Persistent state with reducers for document tracking
- **Memory**: InMemorySaver for maintaining context across sessions
- **Nodes**: Specialized processing nodes for validation, processing, indexing, and generation
- **Human Approval**: Interactive checkpoints for user confirmation

## API Keys

Requires Google API key for Gemini model access. Get your key from [Google AI Studio](https://makersuite.google.com/app/apikey).

## Dependencies

- LangChain & LangGraph for orchestration
- Streamlit for UI
- FAISS for vector storage
- Sentence Transformers for embeddings
- PyPDF for document processing
- Google Generative AI for language model