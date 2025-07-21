"""
Web loader service for loading content from URLs
"""

import streamlit as st
from typing import List
from langchain_core.documents.base import Document
from langchain_community.document_loaders import WebBaseLoader


class WebLoaderService:
    """Service for loading web content from URLs."""
    
    def load_urls(self, urls: List[str]) -> List[List[Document]]:
        """
        Load documents from a list of URLs.
        
        Args:
            urls: List of URLs to load
            
        Returns:
            List of document lists (one list per URL)
        """
        web_docs = []
        progress = st.progress(0)
        
        for i, url in enumerate(urls):
            try:
                with st.spinner(f"Loading {url}..."):
                    docs = self._load_single_url(url)
                    if docs:
                        web_docs.append(docs)
            except Exception as e:
                st.error(f"Error loading {url}: {str(e)}")
            
            # Update progress
            progress.progress((i + 1) / len(urls))
        
        progress.empty()
        return web_docs
    
    def _load_single_url(self, url: str) -> List[Document]:
        """
        Load documents from a single URL.
        
        Args:
            url: URL to load
            
        Returns:
            List of documents from the URL
        """
        try:
            loader = WebBaseLoader(url)
            docs = loader.load()
            return docs
        except Exception as e:
            st.warning(f"Failed to load {url}: {str(e)}")
            return []
    
    def validate_documents(self, docs: List[Document]) -> bool:
        """
        Validate that documents contain content.
        
        Args:
            docs: List of documents to validate
            
        Returns:
            True if documents are valid, False otherwise
        """
        if not docs:
            return False
        
        for doc in docs:
            if doc.page_content and doc.page_content.strip():
                return True
        
        return False