import streamlit as st
from ...schema.state import QueryResponse

class ResultsDisplay:
    def render(self, response):
        if not response:
            st.error("No response to display")
            return

        if isinstance(response, dict):
            try:
                response = QueryResponse(**response)
            except Exception:
                answer_text = response.get("answer") or ""
                st.markdown("#### Answer")
                st.markdown(answer_text)
                return
        
        st.markdown("#### Answer")
        st.markdown(response.answer)
        
        if response.processing_time:
            st.caption(f"Processing time: {response.processing_time:.2f} seconds")
        
        if response.relevant_chunks:
            with st.expander("Source Excerpts", expanded=False):
                for i, chunk in enumerate(response.relevant_chunks):
                    st.markdown(f"**Excerpt {i+1}:**")
                    st.text(chunk)
                    if i < len(response.relevant_chunks) - 1:
                        st.markdown("---")