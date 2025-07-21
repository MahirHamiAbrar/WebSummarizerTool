"""
Text processing utilities for cleaning and formatting text
"""

import strip_markdown


def clean_markdown_response(content: str, model_name: str) -> str:
    """
    Clean markdown formatting from LLM response.
    
    Args:
        content: Raw content from LLM response
        model_name: Name of the model (for model-specific processing)
        
    Returns:
        Cleaned content string
    """
    # Handle markdown code blocks
    if content.startswith('```json'):
        content = content.replace('```json', '```')
    
    # Remove markdown formatting
    cleaned_content = strip_markdown.strip_markdown(content)
    
    # Handle model-specific formatting (e.g., qwen3 thinking tags)
    if 'qwen3' in model_name.lower():
        splits = content.split('</think>')
        if len(splits) > 1:
            # Keep only the part after thinking
            cleaned_content = splits[1].strip()
    
    return cleaned_content


def truncate_text(text: str, max_length: int = 1000) -> str:
    """
    Truncate text to a maximum length.
    
    Args:
        text: Text to truncate
        max_length: Maximum length to keep
        
    Returns:
        Truncated text with ellipsis if needed
    """
    if len(text) <= max_length:
        return text
    
    return text[:max_length - 3] + "..."


def extract_urls_from_text(text: str) -> list:
    """
    Extract URLs from text using regex.
    
    Args:
        text: Text to extract URLs from
        
    Returns:
        List of URLs found in text
    """
    import re
    
    url_pattern = r'https?://(?:[-\w.])+(?:[:\d]+)?(?:/(?:[\w/_.])*(?:\?(?:[\w&=%.])*)?(?:#(?:[\w.])*)?)?'
    urls = re.findall(url_pattern, text)
    return urls


def clean_text_for_display(text: str) -> str:
    """
    Clean text for display in UI.
    
    Args:
        text: Text to clean
        
    Returns:
        Cleaned text suitable for display
    """
    # Remove excessive whitespace
    text = ' '.join(text.split())
    
    # Remove special characters that might break display
    text = text.replace('\x00', '').replace('\r', '\n')
    
    return text.strip()