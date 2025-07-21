"""Tests for service classes."""

import pytest
from unittest.mock import Mock, patch
from src.services.search_service import SearchService
from src.services.web_loader_service import WebLoaderService
from src.services.llm_service import LLMService


class TestSearchService:
    """Test cases for SearchService."""
    
    @patch('src.services.search_service.googlesearch.search')
    @patch('streamlit.spinner')
    def test_search_google(self, mock_spinner, mock_search):
        """Test Google search functionality."""
        mock_search.return_value = ['http://example1.com', 'http://example2.com']
        mock_spinner.return_value.__enter__ = Mock()
        mock_spinner.return_value.__exit__ = Mock()
        
        results = SearchService.search_google('test query', 2)
        assert len(results) == 2
        assert 'http://example1.com' in results
    
    def test_validate_urls(self):
        """Test URL validation."""
        urls = [
            'https://example.com',
            'http://test.com',
            'invalid-url',
            '',
            None
        ]
        
        valid_urls = SearchService.validate_urls(urls)
        assert len(valid_urls) == 2
        assert 'https://example.com' in valid_urls
        assert 'http://test.com' in valid_urls


class TestWebLoaderService:
    """Test cases for WebLoaderService."""
    
    @patch('src.services.web_loader_service.WebBaseLoader')
    def test_load_single_url_success(self, mock_loader):
        """Test successful URL loading."""
        mock_docs = [Mock(page_content='Test content')]
        mock_loader.return_value.load.return_value = mock_docs
        
        service = WebLoaderService()
        docs = service._load_single_url('https://example.com')
        
        assert len(docs) == 1
        assert docs[0].page_content == 'Test content'
    
    def test_validate_documents(self):
        """Test document validation."""
        service = WebLoaderService()
        
        # Valid documents
        valid_docs = [Mock(page_content='Some content')]
        assert service.validate_documents(valid_docs) is True
        
        # Empty documents
        empty_docs = [Mock(page_content='')]
        assert service.validate_documents(empty_docs) is False
        
        # No documents
        assert service.validate_documents([]) is False


class TestLLMService:
    """Test cases for LLMService."""
    
    def test_initialization(self):
        """Test LLM service initialization."""
        service = LLMService()
        assert service.current_model is None
        assert not service.is_initialized()
    
    def test_reset_llm(self):
        """Test LLM reset functionality."""
        service = LLMService()
        service._llm = Mock()
        service._current_model = 'test-model'
        
        service.reset_llm()
        assert service._llm is None
        assert service.current_model is None

