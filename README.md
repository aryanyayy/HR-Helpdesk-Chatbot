# ASKHR — HR Helpdesk Chatbot

An AI-powered HR Helpdesk chatbot built with Python, Streamlit, FastAPI, and Google's Gemini API. ASKHR is a project exploring how employees can interact with HR policy information through a conversational interface.

## Overview

Finding answers to HR questions can involve searching through multiple policy documents. ASKHR aims to simplify this process by providing a chatbot that retrieves relevant policy information and uses an AI model to generate responses.

This project was built as a hands-on exploration of AI integration, backend development, authentication, retrieval, and role-based access control.

## Features

- **Conversational interface:** Chat with the HR Helpdesk through a Streamlit frontend.
- **FastAPI backend:** Handles authentication and chat requests.
- **Gemini integration:** Uses Google's Gemini API to generate responses.
- **Policy retrieval:** Uses local policy data and retrieval components to find relevant information.
- **Role-based access control:** Explores restricting information according to user roles.
- **Environment-based configuration:** Keeps API credentials separate from source code.

## Tech Stack

| Technology | Purpose |
|---|---|
| Python | Application logic |
| Streamlit | User interface |
| FastAPI | Backend API |
| Google Gemini API | AI-generated responses |
| JWT | Authentication tokens |
| CSV | Policy and configuration data |

## Project Structure

```text
ASKHR/
├── app.py
├── .env.example
├── .gitignore
├── requirements.txt
└── backend/
    ├── __init__.py
    ├── main.py
    ├── vector_store.py
    ├── kb_policies_revised.py
    └── [policy data files]
```

The exact data files depend on the version included in the repository.

## Getting Started

### 1. Clone the repository

```bash
git clone https://github.com/aryanyayy/HR-Helpdesk-Chatbot.git
cd HR-Helpdesk-Chatbot
```

### 2. Create a virtual environment

```bash
python -m venv .venv
```

On Windows PowerShell:

```powershell
.\.venv\Scripts\Activate.ps1
```

### 3. Install dependencies

```bash
python -m pip install -r requirements.txt
```

### 4. Configure your API key

Copy `.env.example` to `.env` in the project root.

Add your own Gemini API key to `.env`, using the variable name expected by the backend.

Never commit `.env` or expose API credentials publicly.

### 5. Start the backend

From the project root, run:

```bash
python -m uvicorn backend.main:app --reload --port 8001
```

Keep this terminal open.

### 6. Start the frontend

Open a second terminal in the project root and run:

```bash
python -m streamlit run app.py
```

Open [http://localhost:8501](http://localhost:8501) in your browser.

## Security Notes

- Never publish API keys, passwords, JWT signing secrets, or other credentials.
- Use synthetic or explicitly approved sample data.
- Review role-based access controls before relying on the chatbot for restricted information.
- This project is a learning prototype and has not been presented as a production-ready HR system.

## Current Status

The chatbot has been run locally with the Streamlit frontend and FastAPI backend. Further testing and improvements are needed to validate reliability, authorization, retrieval quality, and error handling.

## Learning Outcomes

- Integrating an external generative AI API
- Building a Python frontend and backend
- Managing environment variables and API credentials
- Exploring retrieval-based question answering
- Implementing authentication and role-based access control
- Debugging API configuration and backend errors

## Author

Developed as a hands-on AI and backend development project.
