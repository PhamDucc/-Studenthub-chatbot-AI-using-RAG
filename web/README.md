# Frontend Documentation

This directory contains the main student portal and the floating AI assistant interface for the Student Hub UET demo.

## Purpose

The frontend provides the user-facing experience for:

- student dashboard and navigation
- profile and academic information
- timetable and class overview
- financial records and service requests
- FAQ pages and chatbot assistance

## Tech stack

- Next.js 16 with App Router
- React 19
- TypeScript
- Tailwind CSS
- shadcn-inspired UI patterns

## Local development

From this folder:

```bash
npm install
npm run dev
```

Then open:

```text
http://localhost:3000
```

## Chat integration

The chat widget sends requests to the local Next.js API route at `/api/chat`, which forwards the payload to the Python backend at `http://127.0.0.1:8000/chat` by default.

The base URL is configurable through:

```bash
export PYTHON_API_URL="http://127.0.0.1:8000"
```

## Important notes

- The frontend is built for demo scenarios and does not include production auth or backend persistence
- Student and academic records are mock data used for presentation
- The chatbot answers are based on the Markdown knowledge base processed by the Python backend

For the full stack setup and environment configuration, see [../README.md](../README.md).
