import time
import json
import ollama
import googlesearch
import strip_markdown
import streamlit as st
from typing import List, Dict, Union

from langchain.chat_models import init_chat_model
from langchain_core.documents.base import Document
from langchain_community.document_loaders import WebBaseLoader

# Set page config
st.set_page_config(
    page_title="Ollama Summarizer",
    page_icon="🔍",
    layout="wide"
)

# Constants from original class
SINGLE_WEBPAGE_SUMMARY_PROMPT = """User wants to know about {query}.
So, Write a concise summary from the following provided context:

{context}
"""
SINGLE_WEBPAGE_SUMMARY_PROMPT = """Summarize the following document: {context}"""

GOOGLE_SEARCH_QUERY_GEN_PROMPT = """You are extremely good at context understanding and generating google search queries based on the understanding.
You are given a user query. Understand what the user wants and generate a perfect, extremely-well-structured google search query that will help the user find what he/she needs.

Generate just the query in JSON format. No extra text. Keys to include: "query".

The user query is following:
{query}
"""

# Modified OllamaSummarizer class for Streamlit integration
class OllamaSummarizer:
    """Class that handles search, webpage loading, and summarization using Ollama models."""

    # Available Ollama models
    model_list: List[str] = [
        model_info["model"]
        for model_info in ollama.list().model_dump()['models']
    ]

    # 'user' role is required for llama models
    system_role = 'user'

    def __init__(self, model_index: int = 0) -> None:
        """
        Initialize the OllamaSummarizer.
        
        Args:
            model_index: Index of the model to use from model_list
        """
        self._web_docs: List[List[Document]] = []
        self._model_name: str = self.model_list[model_index]
        self._llm = None  # Initialize LLM when needed
        
    def initialize_llm(self):
        """Initialize the LLM with the selected model."""
        if self._llm is None:
            with st.spinner(f"Initializing {self._model_name}..."):
                self._llm = init_chat_model(self._model_name, model_provider='ollama')
        return self._llm
    
    def set_model(self, model_index: int) -> None:
        """Change the model being used."""
        self._model_name = self.model_list[model_index]
        self._llm = None  # Reset LLM to reinitialize with new model
    
    def generate_google_search_query(self, user_query: str) -> str:
        """Generate an optimized Google search query based on user input."""
        llm = self.initialize_llm()
        
        with st.spinner("Generating optimized search query..."):
            response = llm.invoke(
                [(
                    self.system_role,
                    GOOGLE_SEARCH_QUERY_GEN_PROMPT.format(query=user_query)
                )]
            )

            # Clean up markdown formatting if present
            if response.content.startswith('```json'):
                response.content = response.content.replace('```json', '```')
            cleaned_content = strip_markdown.strip_markdown(response.content)

            if 'qwen3' in self._model_name:
                splits = response.content.split('</think>')
                chain_of_thoughts = splits[0] + '</think>'
                response.content = splits[1]

            try:
                query_data = json.loads(cleaned_content)
                return query_data['query']
            except json.JSONDecodeError:
                st.warning("Failed to parse optimized query. Using original query instead.")
                return user_query

    def load_urls(self, urls: List[str]) -> None:
        """Load documents from a list of URLs."""
        self._web_docs = []
        progress = st.progress(0)
        
        for i, url in enumerate(urls):
            try:
                with st.spinner(f"Loading {url}..."):
                    docs = WebBaseLoader(url).load()
                    self._web_docs.append(docs)
            except Exception as e:
                st.error(f"Error loading {url}: {str(e)}")
            
            # Update progress
            progress.progress((i + 1) / len(urls))
        
        progress.empty()
    
    def summarize_single_webpage(self, query: str, page_content: str) -> Dict[str, Union[str, dict]]:
        """Summarize the content of a single webpage."""
        llm = self.initialize_llm()
        
        response = llm.invoke(
            [(
                self.system_role,
                # SINGLE_WEBPAGE_SUMMARY_PROMPT.format(query=query, context=page_content)
                SINGLE_WEBPAGE_SUMMARY_PROMPT.format(context=page_content)
            )]
        )

        return {
            'summary': response.content,
            'token_data': response.usage_metadata
        }
    
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
                summary = self.summarize_single_webpage(query, page_content)
                
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
        
        llm = self.initialize_llm()
        
        summaries_text: str = '\n\n'.join(
            f"Summary {i + 1}:\n\t{summary['summary']}"
            for i, summary in enumerate(summaries)
        )

        with st.spinner("Creating final consolidated summary..."):
            result = llm.invoke([
                (self.system_role, """User wants to know about {query}.
And The following is a set of summaries on this topic:
{summaries}

Now, if the query is an asked question then: Generate only an answer to the original query with some useful additional information.
Otherwise: Take these and distill it into a final, consolidated summary of the main themes.
""".format(
        summaries=summaries_text,
        query=query
    ))
            ])

        full_text = result.content
        approx_tokens = result.usage_metadata.get('total_tokens', 0)

        return {
            'summary': full_text,
            'tokens': approx_tokens
        }



"""
Do one of the following two things that fits best according to the original query:
    1. Take these and distill it into a final, consolidated summary of the main themes.
    2. Generate only an answer to the original query.
"""



# Function to search Google and get URLs
def search_google(
    query: str,
    num_results: int = 5,
    unique: bool = True
) -> List[str]:
    """Search Google for URLs based on the query."""
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

# App title and description
st.title("🔍 Ollama Web Summarizer")
st.markdown("""
This app uses Ollama models to search the web, optimize your queries, and generate summaries 
of web content. It works by:
1. Taking your query and optionally optimizing it for search
2. Searching Google for relevant web pages
3. Summarizing each page individually
4. Creating a consolidated summary of all findings
""")

# Sidebar for configuration
st.sidebar.header("Configuration")

# Model selection
model_index = st.sidebar.selectbox(
    "Select Ollama Model",
    range(len(OllamaSummarizer.model_list)),
    format_func=lambda x: OllamaSummarizer.model_list[x]
)

# Search options
optimize_query = st.sidebar.checkbox("Optimize search query with AI", value=True)
num_results = st.sidebar.slider("Number of search results", 1, 10, 5)
unique_results = st.sidebar.checkbox("Return only unique results", value=True)

# Display options
with st.sidebar.expander("Display Options"):
    show_urls = st.checkbox("Show retrieved URLs", value=True)
    show_optimized_query = st.checkbox("Show optimized query", value=True)
    show_individual_summaries = st.checkbox("Show individual summaries", value=True)
    show_token_info = st.checkbox("Show token usage information", value=False)

# Initialize the summarizer with the selected model
summarizer = OllamaSummarizer(model_index)

# Main search form
with st.form("search_form"):
    query = st.text_input("Enter your search query:", "What is agentic RAG?")
    submit_button = st.form_submit_button("Search and Summarize")

# Process search and summarization when the form is submitted
if submit_button:
    # Initialize session state if not already done
    if 'results' not in st.session_state:
        st.session_state.results = {}
    
    # Clear previous results if query changed
    if 'last_query' not in st.session_state or st.session_state.last_query != query:
        st.session_state.results = {}
        st.session_state.last_query = query
    
    # Set the selected model
    summarizer.set_model(model_index)
    
    # Optimize query if selected
    if optimize_query:
        optimized_query = summarizer.generate_google_search_query(query)
        if show_optimized_query:
            st.subheader("Optimized Query")
            st.info(f"Original: '{query}'\nOptimized: '{optimized_query}'")
        search_query = optimized_query
    else:
        search_query = query
    
    # Search for URLs
    urls = search_google(search_query, num_results=num_results, unique=unique_results)
    
    if not urls:
        st.error("No search results found. Please try a different query.")
    else:
        # Display retrieved URLs if enabled
        if show_urls:
            st.subheader("Retrieved URLs")
            for i, url in enumerate(urls):
                st.write(f"{i+1}. [{url}]({url})")
        
        # Load documents from URLs
        with st.spinner("Loading web documents..."):
            summarizer.load_urls(urls)
        
        # Create summaries for each webpage
        st.subheader("Summarizing Webpages")
        summaries = summarizer.summarize_webpages(query)
        
        if not summaries:
            st.error("Failed to generate summaries. Please try again.")
            st.stop()
        
        # Display individual summaries if enabled
        if show_individual_summaries:
            st.subheader("Individual Webpage Summaries")
            for i, summary in enumerate(summaries):
                with st.expander(f"Summary {i+1}: {summary['url']}"):
                    st.markdown(summary['summary'])
                    if show_token_info and 'token_data' in summary:
                        st.caption(f"Tokens: {summary['token_data'].get('total_tokens', 'unknown')}")
        
        # Create final consolidated summary
        st.subheader("Final Consolidated Summary")
        final_summary = summarizer.combine_summaries(query, summaries)
        
        # Display final summary
        st.markdown("### Key Findings")
        st.markdown(final_summary['summary'])
        
        if show_token_info:
            st.caption(f"Tokens for final summary: {final_summary.get('tokens', 0)}")
            
            # Calculate total tokens
            total_tokens = final_summary.get('tokens', 0)
            for summary in summaries:
                if 'token_data' in summary:
                    total_tokens += summary['token_data'].get('total_tokens', 0)
            
            st.info(f"Total tokens used: {total_tokens}")
        
        # Save results to session state
        st.session_state.results = {
            'query': query,
            'optimized_query': optimized_query if optimize_query else None,
            'urls': urls,
            'summaries': [{'url': s['url'], 'summary': s['summary']} for s in summaries],
            'final_summary': final_summary['summary']
        }
        
        st.success("Search and summarization completed successfully!")

# Add download button for results if available
if 'results' in st.session_state and st.session_state.results:
    st.sidebar.header("Export Results")
    
    if st.sidebar.button("Download Results as JSON"):
        results_json = json.dumps(st.session_state.results, indent=2)
        st.sidebar.download_button(
            label="Download JSON",
            data=results_json,
            file_name=f"search_results_{int(time.time())}.json",
            mime="application/json"
        )

# Footer
st.markdown("---")
st.caption("Powered by Ollama and Google Search")
