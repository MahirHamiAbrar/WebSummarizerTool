"""
Page layouts and logic for the Streamlit interface
"""

import streamlit as st
import time
from typing import Dict, Any

from src.services.search_service import SearchService
from src.ui.components import (
    display_urls, 
    display_individual_summaries, 
    display_final_summary, 
    display_token_statistics
)
from src.utils.export_utils import ExportUtils


def render_search_results(query: str, config: Dict, summarizer) -> None:
    """
    Render search results and summaries.
    
    Args:
        query: User search query
        config: Configuration dictionary from sidebar
        summarizer: OllamaSummarizer instance
    """
    # Initialize session state if not already done
    if 'results' not in st.session_state:
        st.session_state.results = {}
    
    # Clear previous results if query changed
    if 'last_query' not in st.session_state or st.session_state.last_query != query:
        st.session_state.results = {}
        st.session_state.last_query = query
    
    # Generate optimized query if enabled
    search_query = query
    optimized_query = None
    
    if config["optimize_query"]:
        optimized_query = summarizer.generate_google_search_query(query)
        if config["show_optimized_query"]:
            st.subheader("Optimized Query")
            st.info(f"Original: '{query}'\nOptimized: '{optimized_query}'")
        search_query = optimized_query
    
    # Perform web search
    search_service = SearchService()
    urls = search_service.search_google(
        search_query, 
        config["num_results"], 
        config["unique_results"]
    )
    
    if not urls:
        st.error("No search results found. Please try a different query.")
        return
    
    # Display URLs if enabled
    if config["show_urls"]:
        display_urls(urls)
    
    # Load and process web content
    _process_web_content(query, urls, config, summarizer, optimized_query)


def _process_web_content(query: str, urls: list, config: Dict, summarizer, optimized_query: str) -> None:
    """
    Process web content and generate summaries.
    
    Args:
        query: Original user query
        urls: List of URLs to process
        config: Configuration dictionary
        summarizer: OllamaSummarizer instance
        optimized_query: Optimized search query (if generated)
    """
    # Load documents from URLs
    with st.spinner("Loading web documents..."):
        summarizer.load_urls(urls)
    
    # Create summaries for each webpage
    st.subheader("Summarizing Webpages")
    summaries = summarizer.summarize_webpages(query)
    
    if not summaries:
        st.error("Failed to generate summaries. Please try again.")
        return
    
    # Display individual summaries if enabled
    if config["show_individual_summaries"]:
        display_individual_summaries(summaries, config["show_token_info"])
    
    # Create and display final consolidated summary
    final_summary = summarizer.combine_summaries(query, summaries)
    display_final_summary(final_summary, config["show_token_info"])
    
    # Display token statistics if enabled
    if config["show_token_info"]:
        display_token_statistics(summaries, final_summary)
    
    # Save results to session state
    _save_results_to_session(query, optimized_query, urls, summaries, final_summary)
    
    st.success("Search and summarization completed successfully!")


def _save_results_to_session(query: str, optimized_query: str, urls: list, summaries: list, final_summary: dict) -> None:
    """
    Save results to session state for export.
    
    Args:
        query: Original query
        optimized_query: Optimized query (if generated)
        urls: List of URLs
        summaries: Individual summaries
        final_summary: Final consolidated summary
    """
    st.session_state.results = {
        'query': query,
        'optimized_query': optimized_query,
        'urls': urls,
        'summaries': [{'url': s['url'], 'summary': s['summary']} for s in summaries],
        'final_summary': final_summary['summary']
    }


def render_export_section() -> None:
    """Render the export and download section."""
    if 'results' not in st.session_state or not st.session_state.results:
        return
    
    st.sidebar.header("Export Results")
    
    export_utils = ExportUtils()
    
    # JSON Export
    if st.sidebar.button("Download Results as JSON"):
        formatted_results = export_utils.format_results_for_export(st.session_state.results)
        results_json = export_utils.to_json_string(formatted_results)
        filename = export_utils.generate_filename(st.session_state.results['query'], 'json')
        
        st.sidebar.download_button(
            label="Download JSON",
            data=results_json,
            file_name=filename,
            mime="application/json"
        )
    
    # Markdown Export
    if st.sidebar.button("Download Results as Markdown"):
        markdown_content = export_utils.create_markdown_export(st.session_state.results)
        filename = export_utils.generate_filename(st.session_state.results['query'], 'md')
        
        st.sidebar.download_button(
            label="Download Markdown",
            data=markdown_content,
            file_name=filename,
            mime="text/markdown"
        )


def render_error_page(error_message: str) -> None:
    """
    Render an error page.
    
    Args:
        error_message: Error message to display
    """
    st.error("⚠️ Application Error")
    st.write(f"**Error:** {error_message}")
    st.write("Please check your configuration and try again.")
    
    if st.button("Refresh Application"):
        st.experimental_rerun()


def render_loading_state(message: str = "Processing...") -> None:
    """
    Render a loading state.
    
    Args:
        message: Loading message to display
    """
    with st.container():
        st.info(f"🔄 {message}")
        st.spinner(message)