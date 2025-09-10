from langchain_google_genai import ChatGoogleGenerativeAI
from ..config.settings import settings

class LLMService:
    def __init__(self):
        self.llm = None
        self._initialize_llm()
    
    def _initialize_llm(self):
        try:
            self.llm = ChatGoogleGenerativeAI(
                model=settings.MODEL_NAME,
                google_api_key=settings.GOOGLE_API_KEY,
                temperature=0.3,
                max_tokens=2048,
                timeout=60,
                max_retries=1
            )
            
        except Exception as e:
            print(f"Failed to initialize LLM: {str(e)}")
            self.llm = None
    
    def is_ready(self) -> bool:
        return self.llm is not None