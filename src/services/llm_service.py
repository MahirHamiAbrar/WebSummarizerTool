"""
LLM service for managing language model interactions
"""

import streamlit as st
from langchain.chat_models import init_chat_model
from config.settings import LLM_CONFIG


class LLMService:
    """Service for managing LLM interactions."""
    
    def __init__(self):
        """Initialize the LLM service."""
        self._llm = None
        self._current_model = None
    
    def get_llm(self, model_name: str):
        """
        Get or initialize the LLM with the specified model.
        
        Args:
            model_name: Name of the model to use
            
        Returns:
            Initialized LLM instance
        """
        if self._llm is None or self._current_model != model_name:
            self._initialize_llm(model_name)
        return self._llm
    
    def _initialize_llm(self, model_name: str):
        """
        Initialize the LLM with the specified model.
        
        Args:
            model_name: Name of the model to use
        """
        try:
            with st.spinner(f"Initializing {model_name}..."):
                self._llm = init_chat_model(
                    model_name, 
                    model_provider=LLM_CONFIG["model_provider"]
                )
                self._current_model = model_name
        except Exception as e:
            st.error(f"Error initializing LLM with model {model_name}: {str(e)}")
            raise e
    
    def reset_llm(self):
        """Reset the LLM to force reinitialization."""
        self._llm = None
        self._current_model = None
    
    @property
    def current_model(self) -> str:
        """Get the current model name."""
        return self._current_model
    
    def is_initialized(self) -> bool:
        """Check if LLM is initialized."""
        return self._llm is not None