#!/usr/bin/env python3
"""
WebSummarizerTool - Main Streamlit Application
Entry point for the web search and summarization tool
"""

import streamlit as st
from src.ui.components import setup_page_config, render_sidebar, render_main_form
from src.ui.pages import render_search_results, render_export_section
from src.models.ollama_summarizer import OllamaSummarizer

def main():
    """Main application entry point"""
    
    # Setup page configuration
    setup_page_config()
    
    # App title and description
    st.title("🔍 Ollama Web Summarizer")
    st.markdown("""
    This app uses Ollama models to search the web, optimize your queries, and generate summaries 
    of web content. It works by:
    1. Taking your query and optionally optimizing it for search
    2. Searching Google for relevant web pages
    3. Summarizing each page individually
    4. Creating a consolidated summary of all findings
    """)
    
    # Initialize the summarizer
    if 'summarizer' not in st.session_state:
        st.session_state.summarizer = OllamaSummarizer()
    
    # Render sidebar configuration
    config = render_sidebar()
    
    # Update summarizer model if changed
    st.session_state.summarizer.set_model(config['model_index'])
    
    # Main search form
    query, submit_button = render_main_form()
    
    # Process search and summarization
    if submit_button and query:
        render_search_results(query, config, st.session_state.summarizer)
    
    # Export section
    render_export_section()
    
    # Footer
    st.markdown("---")
    st.caption("Powered by Ollama and Google Search")

if __name__ == "__main__":
    main()