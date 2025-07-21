"""Tests for utility functions."""

import pytest
from src.utils.text_processing import (
    clean_markdown_response,
    truncate_text,
    extract_urls_from_text,
    clean_text_for_display
)
from src.utils.export_utils import ExportUtils


class TestTextProcessing:
    """Test cases for text processing utilities."""
    
    def test_clean_markdown_response(self):
        """Test markdown cleaning."""
        content = "```json\n{\"test\": \"value\"}\n```"
        result = clean_markdown_response(content, 'test-model')
        assert '```json' not in result
    
    def test_truncate_text(self):
        """Test text truncation."""
        text = "A" * 1000
        result = truncate_text(text, 100)
        assert len(result) == 100
        assert result.endswith('...')
        
        # Test text shorter than limit
        short_text = "Short text"
        result = truncate_text(short_text, 100)
        assert result == short_text
    
    def test_extract_urls_from_text(self):
        """Test URL extraction."""
        text = "Visit https://example.com and http://test.org for more info."
        urls = extract_urls_from_text(text)
        assert len(urls) == 2
        assert 'https://example.com' in urls
        assert 'http://test.org' in urls
    
    def test_clean_text_for_display(self):
        """Test text cleaning for display."""
        messy_text = "  Too   much   whitespace  \r\n"
        result = clean_text_for_display(messy_text)
        assert result == "Too much whitespace"


class TestExportUtils:
    """Test cases for export utilities."""
    
    def test_format_results_for_export(self):
        """Test results formatting for export."""
        results = {
            'query': 'test query',
            'urls': ['http://example.com'],
            'summaries': [{'url': 'http://example.com', 'summary': 'test summary'}],
            'final_summary': 'final summary'
        }
        
        formatted = ExportUtils.format_results_for_export(results)
        
        assert 'metadata' in formatted
        assert 'search_info' in formatted
        assert formatted['search_info']['original_query'] == 'test query'
        assert formatted['search_info']['urls_found'] == 1
    
    def test_generate_filename(self):
        """Test filename generation."""
        query = "What is machine learning?"
        filename = ExportUtils.generate_filename(query, "json")
        
        assert filename.startswith("websummarizer_")
        assert filename.endswith(".json")
        assert "machine" in filename.lower()
    
    def test_create_markdown_export(self):
        """Test markdown export creation."""
        results = {
            'query': 'test query',
            'urls': ['http://example.com'],
            'summaries': [{'url': 'http://example.com', 'summary': 'test summary'}],
            'final_summary': 'final summary'
        }
        
        markdown = ExportUtils.create_markdown_export(results)
        
        assert '# Web Search Summary Report' in markdown
        assert 'test query' in markdown
        assert 'http://example.com' in markdown
        assert 'final summary' in markdown