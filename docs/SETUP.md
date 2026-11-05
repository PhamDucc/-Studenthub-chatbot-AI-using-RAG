# Setup Guide

This guide explains how to run the Student Hub UET demo locally and verify that both the Python API and the Next.js frontend are working.

## Prerequisites

Before starting, make sure the following are installed:

- Python 3.10 or newer
- Node.js 18+ and npm or pnpm
- A terminal with access to the project directory

## 1. Clone and enter the project

```bash
cd /path/to/Studenthub-chatbot
```

## 2. Create a Python environment

```bash
python3 -m venv .venv
source .venv/bin/activate
```

Then install the Python dependencies:

```bash
pip install -r requirements.txt
```

> Note: the repository currently uses a minimal Python dependency set. The demo is intentionally lightweight and relies mainly on the standard library for the backend.

## 3. Prepare the knowledge base

The backend expects Markdown files under the project path:

```text
chatbot/data/
```

If this directory does not exist yet, create it and add your source documents there:

```bash
mkdir -p chatbot/data
```

The retrieval service indexes `*.md` files from that directory. Without source documents, the API will still start but will return no results.

## 4. Start the Python API

From the project root:

```bash
python3 -m backend
```

The service listens on:

- `http://127.0.0.1:8000`

To verify it is alive:

```bash
curl http://127.0.0.1:8000/health
```

Expected response: a JSON object with status and document counts.

## 5. Start the Next.js frontend

Open a second terminal and run:

```bash
cd web
npm install
npm run dev
```

Then open:

```text
http://localhost:3000
```

## 6. Optional: enable Gemini generation

If you want the assistant to synthesize answers from the retrieved documents instead of returning excerpts only, add these environment variables before starting the Python API:

```bash
export GEMINI_API_KEY="your-api-key"
export GEMINI_MODEL="gemini-2.5-flash"
python3 -m backend
```

The frontend can also point to another backend address:

```bash
export PYTHON_API_URL="http://127.0.0.1:8000"
```

## 7. Common troubleshooting

### Backend cannot connect

Make sure the Python process is running and the port is not blocked.

### No answers returned

Check that the Markdown files exist in `chatbot/data` and that they contain readable content.

### Frontend shows API unavailable

Confirm that the Python server is actually running and that `PYTHON_API_URL` points to the correct address.

## Development notes

- The frontend uses Next.js App Router and React 19
- The backend uses Python’s standard library and lightweight lexical retrieval
- This repository is a demo environment; production deployments should include stronger auth, persistence, observability, and deployment configuration
