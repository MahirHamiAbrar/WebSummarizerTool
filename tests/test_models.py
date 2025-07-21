"""Tests for model classes."""

import pytest
from unittest.mock import Mock, patch
from src.models.ollama_summarizer import OllamaSummarizer


class TestOllamaSummarizer:
    """Test cases for OllamaSummarizer class."""
    
    @patch('src.models.ollama_summarizer.ollama.list')
    def test_get_available_models(self, mock_ollama_list):
        """Test getting available models."""
        mock_ollama_list.return_value.model_dump.return_value = {
            'models': [
                {'model': 'llama2:7b'},
                {'model': 'mistral:7b'}
            ]
        }
        
        models = OllamaSummarizer._get_available_models()
        assert len(models) == 2
        assert 'llama2:7b' in models
        assert 'mistral:7b' in models
    
    def test_set_model(self):
        """Test setting model index."""
        with patch.object(OllamaSummarizer, '_get_available_models', return_value=['model1', 'model2']):
            summarizer = OllamaSummarizer()
            summarizer.set_model(1)
            assert summarizer.current_model == 'model2'
