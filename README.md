# Multi-Document Research Assistant

A dynamic, beginner-friendly application for analyzing multiple research documents using Google's Gemini 2.0 Flash model and LangChain. Upload PDFs, ask questions, and get AI-powered insights across all your documents.

## 🚀 Features

- **Multi-Document Processing**: Upload and analyze multiple PDF documents simultaneously
- **Intelligent Chunking**: Smart text splitting for optimal processing
- **Vector Search**: Fast similarity search using FAISS or ChromaDB
- **AI-Powered Answers**: Get comprehensive answers using Gemini 2.0 Flash
- **Interactive UI**: Clean, user-friendly Streamlit interface
- **Advanced Query Options**: Customizable search parameters and query templates
- **Source Citation**: Clear references to source documents
- **Export Capabilities**: Save and export your research results

## 🏗️ Project Structure

```
multi_document_research_assistant/
├── app.py                          # Entry point (3 lines only)
├── requirements.txt                # Dependencies
├── .env                           # Environment variables
├── README.md                      # This file
└── src/
    ├── config/                    # Configuration settings
    ├── schema/                    # Data models
    ├── services/                  # Core business logic
    ├── tools/                     # Processing tools
    ├── utils/                     # Helper utilities
    ├── prompts/                   # AI prompt templates
    └── user_interface/            # Streamlit UI components
```

## 📋 Requirements

- Python 3.8+
- Google API Key (for Gemini model)
- At least 4GB RAM (recommended)
- Internet connection for model access

## 🛠️ Installation

1. **Clone the repository**:
```bash
git clone <your-repo-url>
cd multi_document_research_assistant
```

2. **Install dependencies**:
```bash
pip install -r requirements.txt
```

3. **Set up environment variables**:
   - Copy `.env` file and add your Google API key:
```bash
GOOGLE_API_KEY=your_google_api_key_here
```

4. **Run the application**:
```bash
streamlit run app.py
```

## 🚀 Quick Start

1. **Upload Documents**: 
   - Go to the "Upload Documents" tab
   - Select your PDF files (max 10 files, 200MB each)
   - Click "Process Documents"

2. **Ask Questions**:
   - Switch to "Ask Questions" tab
   - Enter your question or use a template
   - Adjust settings if needed
   - Click "Ask Question"

3. **Review Results**:
   - Read the AI-generated answer
   - Check the source documents
   - Export results if needed

## 💡 Usage Examples

### Research Analysis
```
Question: "What are the main methodologies used across these studies?"
```

### Comparative Analysis  
```
Question: "Compare the conclusions reached by different authors about climate change impacts"
```

### Specific Information
```
Question: "What evidence do the documents provide for the effectiveness of renewable energy?"
```

### Literature Review
```
Question: "Summarize the current state of research on machine learning in healthcare"
```

## ⚙️ Configuration

### Environment Variables (.env)
- `GOOGLE_API_KEY`: Your Google API key for Gemini
- `MODEL_NAME`: Gemini model to use (default: gemini-2.0-flash-exp)
- `CHUNK_SIZE`: Text chunk size (default: 1000)
- `CHUNK_OVERLAP`: Overlap between chunks (default: 200)
- `VECTOR_STORE_TYPE`: Vector store type (faiss/chroma)

### Advanced Settings
- **Chunk Size**: Adjust text chunk sizes (500-2000 characters)
- **Similarity Threshold**: Control relevance filtering (0.0-1.0)
- **Max Results**: Number of sources to retrieve (1-20)

## 🧠 How It Works

1. **Document Processing**: 
   - PDFs are loaded and validated
   - Text is extracted and cleaned
   - Documents are split into manageable chunks

2. **Vector Storage**:
   - Text chunks are converted to embeddings
   - Embeddings are stored in vector database
   - Enables fast similarity search

3. **Query Processing**:
   - User query is embedded
   - Relevant chunks are retrieved
   - Context is provided to AI model

4. **Answer Generation**:
   - Gemini processes query and context
   - Generates comprehensive answer
   - Provides source citations

## 📊 Supported File Types

- **PDF Documents** (.pdf)
  - Research papers
  - Technical documentation  
  - Reports and white papers
  - Books and e-books
  - Academic articles

## 🔧 Customization

### Adding New Document Types
1. Create new loader in `src/services/document_service.py`
2. Update validation in `src/utils/validators.py`
3. Modify UI in `src/user_interface/components/document_uploader.py`

### Custom Prompt Templates
1. Add templates in `src/prompts/templates.py`
2. Update query interface for new templates
3. Modify LLM service to handle new types

### New Vector Stores
1. Implement in `src/services/vector_service.py`
2. Add configuration options
3. Update initialization logic

## 🚨 Troubleshooting

### Common Issues

**"API Key Error"**
- Ensure your Google API key is valid
- Check that Gemini API is enabled
- Verify .env file is properly configured

**"Memory Error"**
- Reduce chunk size or number of documents
- Close other applications
- Consider using cloud deployment

**"PDF Processing Error"**
- Ensure PDFs contain readable text
- Check file isn't password protected
- Try with a different PDF file

**"Vector Store Error"**
- Clear data folder contents
- Restart application
- Check available disk space

### Performance Optimization

- **Large Documents**: Increase chunk size, reduce overlap
- **Many Documents**: Process in smaller batches
- **Slow Queries**: Lower similarity threshold, reduce max results
- **Memory Issues**: Use smaller embedding models

## 🔐 Security Notes

- Store API keys securely (use .env file)
- Don't commit sensitive information to version control
- Consider rate limiting for production use
- Validate all user inputs

## 🚀 Deployment

### Local Development
```bash
streamlit run app.py
```

### Streamlit Cloud
1. Push code to GitHub
2. Connect to Streamlit Cloud
3. Add secrets in dashboard
4. Deploy application

### Docker Deployment
```dockerfile
FROM python:3.9-slim
COPY . /app
WORKDIR /app
RUN pip install -r requirements.txt
EXPOSE 8501
CMD ["streamlit", "run", "app.py"]
```

## 📈 Future Enhancements

- [ ] Support for more file formats (Word, PowerPoint, etc.)
- [ ] Multi-language document support
- [ ] Advanced analytics and visualizations
- [ ] User authentication and document management
- [ ] API endpoints for programmatic access
- [ ] Integration with external databases
- [ ] Custom model fine-tuning capabilities

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙋‍♂️ Support

If you encounter any issues:
1. Check the troubleshooting section
2. Review the logs for error messages
3. Create an issue on GitHub
4. Provide detailed error information

## 🔗 Useful Links

- [Streamlit Documentation](https://docs.streamlit.io/)
- [LangChain Documentation](https://python.langchain.com/)
- [Google AI Documentation](https://ai.google.dev/)
- [FAISS Documentation](https://faiss.ai/)

---

**Happy Research!** 📚✨