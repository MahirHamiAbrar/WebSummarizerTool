"""
Configuration settings and constants for WebSummarizerTool
"""

# Prompt templates
SINGLE_WEBPAGE_SUMMARY_PROMPT = """Summarize the following document: {context}"""

GOOGLE_SEARCH_QUERY_GEN_PROMPT = """You are extremely good at context understanding and generating google search queries based on the understanding.
You are given a user query. Understand what the user wants and generate a perfect, extremely-well-structured google search query that will help the user find what he/she needs.

Generate just the query in JSON format. No extra text. Keys to include: "query".

The user query is following:
{query}
"""

FINAL_SUMMARY_PROMPT = """User wants to know about {query}.
And The following is a set of summaries on this topic:
{summaries}

Now, if the query is an asked question then: Generate only an answer to the original query with some useful additional information.
Otherwise: Take these and distill it into a final, consolidated summary of the main themes.
"""

# App configuration
APP_CONFIG = {
    "page_title": "Ollama Summarizer",
    "page_icon": "🔍",
    "layout": "wide"
}

# Default settings
DEFAULT_SETTINGS = {
    "num_results": 5,
    "unique_results": True,
    "optimize_query": True,
    "show_urls": True,
    "show_optimized_query": True,
    "show_individual_summaries": True,
    "show_token_info": False
}

# Search configuration
SEARCH_CONFIG = {
    "max_results": 10,
    "min_results": 1,
    "default_results": 5
}

# LLM configuration
LLM_CONFIG = {
    "system_role": "user",  # Required for llama models
    "model_provider": "ollama"
}