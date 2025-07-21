"""
Search service for handling Google search functionality
"""

import googlesearch
import streamlit as st
from typing import List


class SearchService:
    """Service for handling web search operations."""
    
    @staticmethod
    def search_google(
        query: str,
        num_results: int = 5,
        unique: bool = True
    ) -> List[str]:
        """
        Search Google for URLs based on the query.
        
        Args:
            query: Search query string
            num_results: Number of results to return
            unique: Whether to return only unique results
            
        Returns:
            List of URLs from search results
        """
        try:
            with st.spinner(f'Searching Google for "{query}"...'):
                links = googlesearch.search(
                    term=query,
                    num_results=num_results,
                    unique=unique
                )
            return [link for link in links]
            
        except Exception as e:
            st.error(f"Error searching Google: {str(e)}")
            return []
    
    @staticmethod
    def validate_urls(urls: List[str]) -> List[str]:
        """
        Validate and filter URLs.
        
        Args:
            urls: List of URLs to validate
            
        Returns:
            List of valid URLs
        """
        valid_urls = []
        for url in urls:
            if url and isinstance(url, str) and url.startswith(('http://', 'https://')):
                valid_urls.append(url)
        return valid_urls