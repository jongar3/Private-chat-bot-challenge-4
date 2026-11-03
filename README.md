# Private-chat-bot-challenge-4
AI agent built with Microsoft Foundry (Code Interpreter, Microsoft Learn MCP server, custom PDF knowledge base) and a Python terminal and web client. Cloud Computing challenge, Master’s in Telecommunications Engineering, Tecnun.

# Microsoft Foundry AI Agent: Cloud Computing Challenge

Project for the **Cloud Computing** course of the **Master's in Telecommunications Engineering** at **Tecnun (Universidad de Navarra)**.

The project builds an AI agent in **Microsoft Foundry** that acts as a Microsoft engineer, helping users create applications with Microsoft technologies such as .NET. A Python client handles authentication and lets users chat with the agent from the terminal or a web interface.

## Features

- **Agent in Microsoft Foundry** using an existing model deployed in the Foundry project
- **System instructions** that define the agent as a Microsoft engineer who helps build applications with Microsoft technology
- **Code Interpreter** to run code, do calculations and generate charts
- **MCP server integration:** [Microsoft Learn MCP server](https://learn.microsoft.com/api/mcp), so Microsoft product questions are answered from accurate, up-to-date documentation
- **Custom data:** sample PDF documents (generated with GenAI) indexed with Azure AI Search and connected to the agent as a knowledge base
- **Web interface** built with Streamlit

## Architecture

```
User ──► Python client (terminal / Streamlit)
              │  Azure authentication (browser login or Azure CLI)
              ▼
        Microsoft Foundry project
              │
              ▼
          AI Agent ──► Model deployment
              ├──► Code Interpreter
              ├──► Microsoft Learn MCP server
              └──► Azure AI Search index (PDF documents)
```

## Project structure

## Setup

```bash
# 1. Clone the repository
git clone https://github.com/<your-user>/<your-repo>.git
cd <your-repo>

# 2. Create and activate a virtual environment
python -m venv venv
venv\Scripts\activate        # Windows
# source venv/bin/activate   # macOS / Linux

# 3. Install dependencies
pip install -r requirements.txt

```

## Authentication

The client uses `DefaultAzureCredential` (for example after `az login`) and falls back to an interactive browser login. No secrets in the code.

## Usage

**Terminal:**

```bash
python chat.py
```

**Web interface:**

```bash
streamlit run web.py
```

## Agent configuration

**Instructions:**

> You are a Microsoft engineer. You must assist and help create applications with Microsoft technology such as .NET, answer questions, etc. Please direct all Microsoft product related queries to the Microsoft Learn MCP server for accurate and up-to-date documentation. When answering from the PDFs, say which document the answer came from.
