# AI Content Detector for Teachers - Production Telegram Bot

This is a production-ready, asynchronous Telegram bot designed for teachers to detect AI-generated student assignments. It uses a hybrid analysis engine that combines OpenAI's Structured Outputs API with local statistical metrics (perplexity, burstiness, and sentence length variance).

## 🚀 Features
- **Hybrid Detection:** Combines GPT-4o-mini processing with localized text statistical heuristics.
- **Multi-Format Processing:** Supports direct copy-pasted text, or `.txt`, `.pdf`, and `.docx` documents.
- **Role-Based Plan Constraints:** Features a built-in subscription middleware module (Free tier limited to 5 daily text checks; Premium tier scales to process documents).
- **Export System:** Generates clear text or PDF forensic summaries natively.

## 🛠️ Local Quickstart Initialization Setup

1. **Clone project structure and construct configuration file variables:**
   ```bash
   cp .env.example .env
