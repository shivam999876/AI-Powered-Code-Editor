# AI-Powered Code Editor

A Streamlit application that provides an AI-powered code editor with the following features:

- Write, execute, and manage code in multiple languages (Python, JavaScript, Java, C++)
- AI assistance for coding tasks using Gemini Pro
- Custom tools for file and folder management
- Web search capability

## Requirements

- Python 3.x
- Required packages:
  - streamlit
  - langchain
  - langchain-google-genai
  - langchain-community
  - python-dotenv
  - tavily-python

## Setup

1. Clone this repository
2. Create a virtual environment: `python -m venv venv`
3. Activate the virtual environment:
   - Windows: `venv\Scripts\activate`
   - Linux/Mac: `source venv/bin/activate`
4. Install dependencies: `pip install -r requirements.txt`
5. Create a `.env` file with your API keys:
   ```
   GEMINI_API_KEY=your_gemini_api_key
   TAVILY_API_KEY=your_tavily_api_key
   ```
6. Run the application: `streamlit run app.py`

## Features

- Multi-language code execution
- AI-powered assistance
- File and folder management
- Web search integration

## License

MIT