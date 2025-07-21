"""
OllamaSummarizer class - Core model for web search optimization and summarization
"""

import json
import ollama
import streamlit as st
from typing import List, Dict, Union

from langchain.chat_models import init_chat_model
from langchain_core.documents.base import Document

from config.settings import (
    SINGLE_WEBPAGE_SUMMARY_PROMPT,
    GOOGLE_SEARCH_QUERY_GEN_PROMPT, 
    FINAL_SUMMARY_PROMPT,
    LLM_CONFIG
)
from src.services.llm_service import LLMService
from src.services.web_loader_service import WebLoaderService
from src.utils.text_processing import clean_markdown_response


class OllamaSummarizer:
    """Class that handles search, webpage loading, and summarization using Ollama models."""

    def __init__(self, model_index: int = 0) -> None:
        """
        Initialize the OllamaSummarizer.
        
        Args:
            model_index: Index of the model to use from model_list
        """
        self._web_docs: List[List[Document]] = []
        self._model_list = self._get_available_models()
        self._model_name = self._model_list[model_index] if self._model_list else None
        
        # Initialize services
        self.llm_service = LLMService()
        self.web_loader_service = WebLoaderService()
        
    @staticmethod
    def _get_available_models() -> List[str]:
        """Get list of available Ollama models."""
        try:
            return [
                model_info["model"]
                for model_info in ollama.list().model_dump()['models']
            ]
        except Exception as e:
            st.error(f"Error fetching Ollama models: {str(e)}")
            return []
    
    @property
    def model_list(self) -> List[str]:
        """Get the list of available models."""
        return self._model_list
    
    @property
    def current_model(self) -> str:
        """Get the current model name."""
        return self._model_name
        
    def set_model(self, model_index: int) -> None:
        """Change the model being used."""
        if 0 <= model_index < len(self._model_list):
            self._model_name = self._model_list[model_index]
            self.llm_service.reset_llm()  # Reset LLM to reinitialize with new model
    
    def generate_google_search_query(self, user_query: str) -> str:
        """Generate an optimized Google search query based on user input."""
        with st.spinner("Generating optimized search query..."):
            try:
                llm = self.llm_service.get_llm(self._model_name)
                
                response = llm.invoke([
                    (LLM_CONFIG["system_role"], 
                     GOOGLE_SEARCH_QUERY_GEN_PROMPT.format(query=user_query))
                ])

                cleaned_content = clean_markdown_response(response.content, self._model_name)

                query_data = json.loads(cleaned_content)
                return query_data['query']
                
            except json.JSONDecodeError:
                st.warning("Failed to parse optimized query. Using original query instead.")
                return user_query
            except Exception as e:
                st.error(f"Error generating optimized query: {str(e)}")
                return user_query

    def load_urls(self, urls: List[str]) -> None:
        """Load documents from a list of URLs."""
        self._web_docs = self.web_loader_service.load_urls(urls)
    
    def summarize_single_webpage(self, page_content: str) -> Dict[str, Union[str, dict]]:
        """Summarize the content of a single webpage."""
        try:
            llm = self.llm_service.get_llm(self._model_name)
            
            response = llm.invoke([
                (LLM_CONFIG["system_role"], 
                 SINGLE_WEBPAGE_SUMMARY_PROMPT.format(context=page_content))
            ])

            return {
                'summary': response.content,
                'token_data': getattr(response, 'usage_metadata', {})
            }
        except Exception as e:
            st.error(f"Error summarizing webpage: {str(e)}")
            return {'summary': "Error generating summary", 'token_data': {}}
    
    def summarize_webpages(self, query: str) -> List[Dict[str, Union[str, dict]]]:
        """Summarize all loaded webpages."""
        if not self._web_docs:
            return []
        
        summaries = []
        progress = st.progress(0)
        
        for i, doc_list in enumerate(self._web_docs):
            try:
                # Extract metadata for the URL
                url = doc_list[0].metadata.get('source', 'Unknown URL')
                st.text(f"Summarizing: {url}")
                
                # Get the content and summarize
                page_content = "\n\n".join([doc.page_content for doc in doc_list])
                summary = self.summarize_single_webpage(page_content)
                
                # Add URL to summary data
                summary['url'] = url
                summaries.append(summary)
                
            except Exception as e:
                st.error(f"Error summarizing document {i+1}: {str(e)}")
            
            # Update progress
            progress.progress((i + 1) / len(self._web_docs))
        
        progress.empty()
        return summaries
    
    def combine_summaries(self, query: str, summaries: List[Dict[str, Union[str, dict]]]) -> Dict[str, Union[str, int]]:
        """Combine multiple summaries into a final consolidated summary."""
        if not summaries:
            return {'summary': "No summaries available to combine.", 'tokens': 0}
        
        try:
            llm = self.llm_service.get_llm(self._model_name)
            
            summaries_text = '\n\n'.join(
                f"Summary {i + 1}:\n\t{summary['summary']}"
                for i, summary in enumerate(summaries)
            )

            with st.spinner("Creating final consolidated summary..."):
                result = llm.invoke([
                    (LLM_CONFIG["system_role"], 
                     FINAL_SUMMARY_PROMPT.format(
                         summaries=summaries_text,
                         query=query
                     ))
                ])

            return {
                'summary': result.content,
                'tokens': getattr(result, 'usage_metadata', {}).get('total_tokens', 0)
            }
            
        except Exception as e:
            st.error(f"Error combining summaries: {str(e)}")
            return {'summary': "Error generating final summary", 'tokens': 0}