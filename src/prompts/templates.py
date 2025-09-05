class PromptTemplates:
    """Collection of prompt templates for different use cases"""
    
    RESEARCH_QA_TEMPLATE = """
        You are a helpful research assistant that answers questions based on the provided context from multiple documents.

        Context from documents:
        {context}

        Question: {question}

        Instructions:
        1. Answer the question based ONLY on the information provided in the context
        2. If the context doesn't contain enough information to answer the question, say so clearly
        3. Provide a comprehensive answer that synthesizes information from multiple sources if available
        4. Be precise and factual in your response

        Answer:
    """

    EXTRACTION_TEMPLATE = """
        Extract specific information from the provided documents.

        Context:
        {context}

        What to extract: {extraction_query}

        Please extract the requested information and organize it clearly:
    """

    FACT_CHECK_TEMPLATE = """
        You are fact-checking information across multiple documents.

        Context from documents:
        {context}

        Claim to verify: {claim}

        Please:
        1. Verify if the claim is supported by the documents
        2. Note any contradictory information
        3. Rate the reliability of the information

        Fact-check result:
    """

    @staticmethod
    def get_template(template_type: str = "research_qa") -> str:
        """Get a specific prompt template"""
        templates = {
            "research_qa": PromptTemplates.RESEARCH_QA_TEMPLATE,
            "extraction": PromptTemplates.EXTRACTION_TEMPLATE,
            "fact_check": PromptTemplates.FACT_CHECK_TEMPLATE
        }
        return templates.get(template_type, PromptTemplates.RESEARCH_QA_TEMPLATE)

    @staticmethod
    def format_context(retrieved_chunks: list) -> str:
        """Format retrieved chunks into context string"""
        context_parts = []
        for i, chunk in enumerate(retrieved_chunks, 1):
            source_info = chunk.metadata.get('source', 'Unknown Document')
            page_info = chunk.metadata.get('page', 'Unknown Page')
            
            context_part = f"""
                --- Source {i}: {source_info} (Page: {page_info}) ---
                {chunk.page_content}
            """
            context_parts.append(context_part)
        
        return "\n".join(context_parts)