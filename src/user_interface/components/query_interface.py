from typing import Any, Dict, Optional
import streamlit as st
from ...utils.validators import validate_query

class QueryInterface:
    def render(self) -> Optional[Dict[str, Any]]:
        query = st.text_area(
            "Enter your question:",
            placeholder="e.g., What are the main findings about climate change impacts?",
            height=100,
            help="Ask any question about your uploaded documents"
        )
        
        if st.button("Ask Question", type="primary", use_container_width=True):
            if query:
                validation_result = validate_query(query)
                
                if not validation_result.is_valid:
                    st.error(f"{validation_result.error_message}")
                    return None
                
                for warning in validation_result.warnings:
                    st.warning(f"{warning}")
                
                return {
                    'question': query.strip(),
                    'max_results': 5
                }
            else:
                st.warning("Please enter a question before submitting.")
        
        return None