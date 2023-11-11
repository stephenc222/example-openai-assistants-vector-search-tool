# Enhancing GPT Assistants with Vector Search Tools

## Overview

This GitHub companion repository accompanies my [blog post](http://stephencollins.tech/posts/enhancing-gpt-assistants-with-vector-search-tools) "Enhancing GPT Assistants with Vector Search Tools" which details the process of integrating custom vector search tools with OpenAI's GPT Assistants. The integration enables GPT Assistants to provide contextually nuanced responses for an improved user experience. The tutorial guides you through creating a 'VectorizedKnowledgeBot' that leverages vector-based searches to deliver precise information retrieval.

## Prerequisites

- OpenAI API Key stored in a `.env` file
- Python 3.9
- Python packages: `torch==2.1.0`, `transformers==4.34.0`, `sqlean.py`, `python-dotenv`, `openai`

## Setup

Create a `.env` file with your OpenAI API key:

```bash
OPENAI_API_KEY=your_api_key_here
```

Install the required Python dependencies.

## Tool: `vector_search`

The `vector_search.py` script performs a vector-based search using an sqlite database with `sqlite-vss`. It processes a query string to retrieve relevant data from a virtual table, `vss_posts`.

## Application: `app.py`

The `app.py` script initializes a test database, incorporates the `vector_search` tool, and sets up an interaction with a GPT Assistant. It includes instructions for the Assistant to perform vector-based searches and handle user prompts.

## Running the Bot

Execute the `main()` function within `app.py` to start the bot. The function handles database setup, Assistant creation, message handling, and tool invocation.

## Error Handling

The script includes error handling to manage any exceptions during execution and asynchronous operations to monitor the Assistant's status.

## Conclusion

Following the tutorial should result in a functional VectorizedKnowledgeBot that enhances the capabilities of GPT Assistants using vector search tools.
