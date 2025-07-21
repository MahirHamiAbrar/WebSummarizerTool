"""
Export and download utilities for saving results
"""

import json
import time
from typing import Dict, Any


class ExportUtils:
    """Utility class for exporting and downloading results."""
    
    @staticmethod
    def format_results_for_export(results: Dict[str, Any]) -> Dict[str, Any]:
        """
        Format results for export.
        
        Args:
            results: Results dictionary to format
            
        Returns:
            Formatted results dictionary
        """
        formatted = {
            "metadata": {
                "export_timestamp": time.time(),
                "export_date": time.strftime("%Y-%m-%d %H:%M:%S"),
                "tool_name": "WebSummarizerTool"
            },
            "search_info": {
                "original_query": results.get('query', ''),
                "optimized_query": results.get('optimized_query', ''),
                "urls_found": len(results.get('urls', []))
            },
            "urls": results.get('urls', []),
            "individual_summaries": results.get('summaries', []),
            "final_summary": results.get('final_summary', ''),
            "statistics": {
                "total_sources": len(results.get('summaries', [])),
                "final_summary_length": len(results.get('final_summary', ''))
            }
        }
        return formatted
    
    @staticmethod
    def to_json_string(data: Dict[str, Any], indent: int = 2) -> str:
        """
        Convert data to JSON string.
        
        Args:
            data: Data to convert
            indent: JSON indentation level
            
        Returns:
            JSON string
        """
        return json.dumps(data, indent=indent, ensure_ascii=False)
    
    @staticmethod
    def generate_filename(query: str, file_type: str = "json") -> str:
        """
        Generate a filename for export.
        
        Args:
            query: Original search query
            file_type: File extension (without dot)
            
        Returns:
            Generated filename
        """
        # Clean query for filename
        clean_query = "".join(c for c in query if c.isalnum() or c in (' ', '-', '_')).rstrip()
        clean_query = clean_query.replace(' ', '_')[:50]  # Limit length
        
        timestamp = int(time.time())
        return f"websummarizer_{clean_query}_{timestamp}.{file_type}"
    
    @staticmethod
    def create_markdown_export(results: Dict[str, Any]) -> str:
        """
        Create markdown formatted export.
        
        Args:
            results: Results to format
            
        Returns:
            Markdown formatted string
        """
        md_content = f"""# Web Search Summary Report

**Generated:** {time.strftime("%Y-%m-%d %H:%M:%S")}
**Tool:** WebSummarizerTool

## Search Query
**Original Query:** {results.get('query', 'N/A')}
**Optimized Query:** {results.get('optimized_query', 'Same as original')}

## Sources Found
"""
        
        urls = results.get('urls', [])
        for i, url in enumerate(urls, 1):
            md_content += f"{i}. [{url}]({url})\n"
        
        md_content += "\n## Individual Summaries\n\n"
        
        summaries = results.get('summaries', [])
        for i, summary in enumerate(summaries, 1):
            url = summary.get('url', 'Unknown URL')
            content = summary.get('summary', 'No summary available')
            md_content += f"### Source {i}: {url}\n\n{content}\n\n"
        
        md_content += "## Final Consolidated Summary\n\n"
        md_content += results.get('final_summary', 'No final summary available')
        
        return md_content