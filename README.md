# WebSummarizerTool

A powerful web search and summarization tool that uses Ollama models to optimize search queries, retrieve web content, and generate comprehensive summaries.

## Features

- **AI-Powered Query Optimization**: Automatically improves your search queries for better results
- **Multi-Source Summarization**: Fetches and summarizes content from multiple web sources
- **Consolidated Summaries**: Combines individual summaries into comprehensive final reports
- **Multiple Export Formats**: Export results as JSON or Markdown
- **Configurable Models**: Choose from available Ollama models
- **User-Friendly Interface**: Built with Streamlit for easy interaction

## Installation

1. **Prerequisites**:
   - Python 3.8 or higher
   - [Ollama](https://ollama.ai/) installed and running
   - At least one Ollama model downloaded (e.g., `ollama pull llama2`)

2. **Install the package**:
   ```bash
   pip install -r requirements.txt
   ```

## Usage

### Running the Application

```bash
streamlit run main.py
```

The application will open in your web browser at `http://localhost:8501`.

### Using the Interface

1. **Select Model**: Choose from available Ollama models in the sidebar
2. **Configure Search**: Set number of results and search options
3. **Enter Query**: Type your search query in the main input field
4. **Review Results**: View individual summaries and the final consolidated summary
5. **Export Results**: Download results in JSON or Markdown format

## Project Structure

```
WebSummarizerTool/
├── main.py                          # Streamlit app entry point
├── requirements.txt                 # Project dependencies
├── config/
│   └── settings.py                  # Configuration and constants
├── src/
│   ├── models/
│   │   └── ollama_summarizer.py     # Core summarization logic
│   ├── services/
│   │   ├── search_service.py        # Google search functionality
│   │   ├── web_loader_service.py    # Web content loading
│   │   └── llm_service.py          # LLM interaction service
│   ├── utils/
│   │   ├── text_processing.py       # Text processing utilities
│   │   └── export_utils.py         # Export/download utilities
│   └── ui/
│       ├── components.py           # Reusable UI components
│       └── pages.py               # Page layouts and logic
└── tests/
    ├── test_models.py
    ├── test_services.py
    └── test_utils.py
```

## Configuration

### Environment Variables

Create a `.env` file (optional) for environment-specific settings:

```env
# Example environment variables
OLLAMA_HOST=http://localhost:11434
DEFAULT_MODEL=llama2:7b
MAX_SEARCH_RESULTS=10
```

### Custom Prompts

Modify prompts in `config/settings.py` to customize the AI behavior:

- `SINGLE_WEBPAGE_SUMMARY_PROMPT`: Controls individual page summarization
- `GOOGLE_SEARCH_QUERY_GEN_PROMPT`: Controls query optimization
- `FINAL_SUMMARY_PROMPT`: Controls final summary generation

## Development

### Running Tests

```bash
pytest
```

### Code Structure

The application follows a modular architecture:

- **Models**: Core business logic and data structures
- **Services**: External integrations (search, web loading, LLM)
- **Utils**: Helper functions and utilities
- **UI**: Streamlit interface components and pages

### Adding New Features

1. **New Services**: Add to `src/services/`
2. **New Models**: Add to `src/models/`
3. **New UI Components**: Add to `src/ui/components.py`
4. **New Pages**: Add to `src/ui/pages.py`

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Troubleshooting

### Common Issues

1. **No Ollama models found**:
   - Ensure Ollama is running: `ollama serve`
   - Download a model: `ollama pull llama2`

2. **Search results not loading**:
   - Check internet connection
   - Verify Google search is not blocked

3. **Summarization errors**:
   - Try a different Ollama model
   - Reduce the number of search results
   - Check Ollama logs for errors

### Performance Tips

- Use lighter models (e.g., `llama2:7b`) for faster processing
- Reduce the number of search results for quicker execution
- Enable query optimization for better search results