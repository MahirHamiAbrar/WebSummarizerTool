"""
Reusable UI components for the Streamlit interface
"""

import streamlit as st
from typing import Dict, Tuple
from config.settings import APP_CONFIG, DEFAULT_SETTINGS, SEARCH_CONFIG
from src.models.ollama_summarizer import OllamaSummarizer


def setup_page_config():
    """Setup Streamlit page configuration."""
    st.set_page_config(**APP_CONFIG)


def render_sidebar() -> Dict:
    """
    Render the sidebar with configuration options.
    
    Returns:
        Dictionary containing all configuration settings
    """
    st.sidebar.header("Configuration")
    
    # Model selection
    if 'summarizer' in st.session_state:
        model_list = st.session_state.summarizer.model_list
    else:
        model_list = OllamaSummarizer()._get_available_models()
    
    if not model_list:
        st.sidebar.error("No Ollama models found. Please install Ollama and download models.")
        return {}
    
    model_index = st.sidebar.selectbox(
        "Select Ollama Model",
        range(len(model_list)),
        format_func=lambda x: model_list[x]
    )
    
    # Search options
    st.sidebar.subheader("Search Options")
    optimize_query = st.sidebar.checkbox("Optimize search query with AI", DEFAULT_SETTINGS["optimize_query"])
    num_results = st.sidebar.slider(
        "Number of search results", 
        SEARCH_CONFIG["min_results"], 
        SEARCH_CONFIG["max_results"], 
        SEARCH_CONFIG["default_results"]
    )
    unique_results = st.sidebar.checkbox("Return only unique results", DEFAULT_SETTINGS["unique_results"])
    
    # Display options
    with st.sidebar.expander("Display Options"):
        show_urls = st.checkbox("Show retrieved URLs", DEFAULT_SETTINGS["show_urls"])
        show_optimized_query = st.checkbox("Show optimized query", DEFAULT_SETTINGS["show_optimized_query"])
        show_individual_summaries = st.checkbox("Show individual summaries", DEFAULT_SETTINGS["show_individual_summaries"])
        show_token_info = st.checkbox("Show token usage information", DEFAULT_SETTINGS["show_token_info"])
    
    return {
        "model_index": model_index,
        "optimize_query": optimize_query,
        "num_results": num_results,
        "unique_results": unique_results,
        "show_urls": show_urls,
        "show_optimized_query": show_optimized_query,
        "show_individual_summaries": show_individual_summaries,
        "show_token_info": show_token_info
    }


def render_main_form() -> Tuple[str, bool]:
    """
    Render the main search form.
    
    Returns:
        Tuple of (query, submit_button_pressed)
    """
    with st.form("search_form"):
        query = st.text_input("Enter your search query:", "What is agentic RAG?")
        submit_button = st.form_submit_button("Search and Summarize")
    
    return query, submit_button


def display_urls(urls: list, title: str = "Retrieved URLs"):
    """Display a list of URLs in an organized format."""
    st.subheader(title)
    for i, url in enumerate(urls):
        st.write(f"{i+1}. [{url}]({url})")


def display_individual_summaries(summaries: list, show_token_info: bool = False):
    """Display individual webpage summaries in expandable sections."""
    st.subheader("Individual Webpage Summaries")
    for i, summary in enumerate(summaries):
        with st.expander(f"Summary {i+1}: {summary['url']}"):
            st.markdown(summary['summary'])
            if show_token_info and 'token_data' in summary:
                st.caption(f"Tokens: {summary['token_data'].get('total_tokens', 'unknown')}")


def display_final_summary(final_summary: dict, show_token_info: bool = False):
    """Display the final consolidated summary."""
    st.subheader("Final Consolidated Summary")
    st.markdown("### Key Findings")
    st.markdown(final_summary['summary'])
    
    if show_token_info:
        st.caption(f"Tokens for final summary: {final_summary.get('tokens', 0)}")


def display_token_statistics(summaries: list, final_summary: dict):
    """Display comprehensive token usage statistics."""
    total_tokens = final_summary.get('tokens', 0)
    for summary in summaries:
        if 'token_data' in summary:
            total_tokens += summary['token_data'].get('total_tokens', 0)
    
    st.info(f"Total tokens used: {total_tokens}")