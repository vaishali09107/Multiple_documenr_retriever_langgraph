import streamlit as st
from typing import Optional, Dict, Any
from ...utils.validators import validate_query

class QueryInterface:
    """Component for handling user queries"""
    
    def render(self) -> Optional[Dict[str, Any]]:
        """Render the query interface""" 
        query = self._render_free_text_input()
        
        if st.button("Ask Question", type="primary", use_container_width=True):
            if query:
                return {
                    'question': query,
                    'max_results': 5
                }
            else:
                st.warning("Please enter a question before submitting.")
        return None
    
    def _render_free_text_input(self) -> Optional[str]:
        """Render free text input for queries"""
        
        query = st.text_area(
            "Enter your question:",
            placeholder="e.g., What are the main findings about climate change impacts?",
            height=100,
            help="Ask any question about your uploaded documents"
        )
        
        if query:
            validation_result = validate_query(query)
            
            if not validation_result.is_valid:
                st.error(f"{validation_result.error_message}")
                return None
            
            for warning in validation_result.warnings:
                st.warning(f"{warning}")
            
            return query.strip()
        
        return None
    
    def _show_example_queries(self):
        """Deprecated: previously showed static example queries (now removed)."""
        return