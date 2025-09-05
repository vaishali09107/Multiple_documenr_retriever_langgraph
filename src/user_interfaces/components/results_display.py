import streamlit as st
from typing import List, Dict, Any
from ...schema.models import QueryResponse

class ResultsDisplay:
    """Component for displaying query results"""
    
    def render(self, response: QueryResponse):
        """Render the query results"""
        
        if not response:
            st.error("No response to display")
            return
        
        self._render_main_answer(response)
    
    def _render_main_answer(self, response: QueryResponse):
        """Render the main answer"""
        
        st.markdown("Answer")
        st.markdown(response.answer)
        