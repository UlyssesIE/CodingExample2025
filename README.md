# CodingExample2025

This repository contains two Python backend services designed to power intelligent information retrieval for frontend applications. Both services are projects I completed in real world companies with some edition in configurations. These services interact with a vector database (Elasticsearch) to find relevant information based on user questions, construct prompts for Large Language Models (LLMs), and stream the LLM's responses back to the frontend. One service utilizes Server-Sent Events (SSE) for streaming, while the other employs WebSockets.


**Features**

_Vector Database Search (Elasticsearch)_: The backend service queries Elasticsearch (acting as a vector database) to find documents or information semantically similar to the user's question.

_LLM Prompt Construction_: The retrieved information is used to construct a comprehensive prompt for an LLM. This prompt typically includes the user's question and the context from Elasticsearch.

_LLM Interaction_: The prompt is sent to an LLM (e.g., OpenAI GPT, Google Gemini, etc. - specify if you're using a particular one).

_Streaming Output: The LLM's response is streamed back to the frontend using either SSE or WebSockets, providing a continuous flow of information as it becomes available._

**Installation**

To run these services, you need an available Elasticsearch vector database and LLM interface. You can replace the IP address of vector database and LLM in the config.py to implement your setting.

The original services are designed for deepseek-r1, if you want to try other LLM, you may need to change the structure of post message in api.py.

Please use the following command to install all required packages:

`pip install -r requirements.txt`
