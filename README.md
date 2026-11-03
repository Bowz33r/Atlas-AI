# Atlas — Personal Python AI Agent

A local-first personal AI assistant with a browser dashboard, account setup, persistent chat memory, workspace file tools, optional web search, and a restricted Python runner.

## Quick start (Windows 10/11)
1. Install Python 3.11+ from https://www.python.org/downloads/ (enable **Add Python to PATH**).
2. Optional local AI: install Ollama from https://ollama.com/ then run `ollama pull qwen2.5:7b`.
3. Double-click `run_windows.bat`.
4. Open http://127.0.0.1:8000 and create your administrator password.
5. Start chatting.

Mac/Linux: run `chmod +x run_mac_linux.sh && ./run_mac_linux.sh`, then open the same address.

## AI providers
- **Ollama (default/local):** start Ollama and pull the model shown in `.env`. Change `OLLAMA_MODEL` to another model you have pulled.
- **OpenAI-compatible:** set `AI_PROVIDER=openai_compatible`, `AI_BASE_URL`, `AI_API_KEY`, and `AI_MODEL` in `.env`. Keep API keys private; never put them in browser code.

If no model is available, the app still starts and explains how to connect one.

## What it can do
- Chat with a configured AI model.
- Remember conversation history in local SQLite.
- Read/write text files inside `workspace/`.
- Run Python scripts inside `workspace/` with a timeout and output limit.
- Optional DuckDuckGo search if you install `ddgs` (`pip install ddgs`).
- Browser speech recognition/speech synthesis where supported.
- Export chat history from the dashboard.

## Security notes — read before exposing it
- The server binds to `127.0.0.1` only. Do not change this to `0.0.0.0` or expose it to the internet without adding HTTPS, rate limiting, CSRF protection, hardened session storage, and a proper deployment review.
- First-run account setup creates a password hash. Passwords are never stored in plain text.
- Python execution is **not a secure operating-system sandbox**. It is intended for your own local use, has a timeout, and is limited to the workspace as its working directory, but Python can still access files and the network with the server user's permissions. Only run code you trust. For stronger isolation, run the app in a dedicated Windows Sandbox/VM or container with no sensitive mounts.
- AI-generated actions are not automatically executed. Python execution and file writes require a direct user action in the interface.
- Keep `.env`, `data/`, and `workspace/` private. Back them up securely.
- This starter does not autonomously click around your desktop, send emails, make purchases, or execute arbitrary shell commands.

## Project layout
- `app/main.py` — FastAPI routes and agent logic
- `app/security.py` — password hashing and signed session cookie
- `app/store.py` — SQLite users, messages and memory
- `app/agent.py` — provider adapters, tool routing, safe workspace helpers
- `app/static/` — dashboard UI
- `workspace/` — files the agent is allowed to manage

## Troubleshooting
- `ollama` connection error: start Ollama, run `ollama pull qwen2.5:7b`, and check `OLLAMA_BASE_URL`.
- Hosted model error: verify provider URL, model name and API key in `.env`, then restart.
- Port in use: change `--port 8000` in the run command and open that port locally.
