import os, json, pathlib, subprocess, sys
import httpx

WORKSPACE = pathlib.Path(os.getenv("WORKSPACE_DIR", "./workspace")).resolve()
WORKSPACE.mkdir(parents=True, exist_ok=True)
SYSTEM = '''You are Atlas, a capable personal AI assistant. Be honest about uncertainty and tool limits.
You can plan, explain, draft, research when search is available, and help with programming.
Do not claim you ran code, changed files, browsed, or completed an action unless a tool result confirms it.
For risky, destructive, financial, or external actions, explain the risks and ask the user to do/approve them.
Python and file tools are available only through explicit dashboard actions, not automatically.
Keep answers practical and structured.'''

def safe_path(name: str) -> pathlib.Path:
    p = (WORKSPACE / name).resolve()
    if p != WORKSPACE and WORKSPACE not in p.parents:
        raise ValueError("Path must stay inside the workspace folder.")
    return p

async def ask_model(messages):
    provider = os.getenv("AI_PROVIDER", "ollama").lower()
    if provider == "openai_compatible":
        base = os.getenv("AI_BASE_URL", "https://api.openai.com/v1").rstrip("/")
        key = os.getenv("AI_API_KEY", "")
        model = os.getenv("AI_MODEL", "gpt-4o-mini")
        if not key: raise RuntimeError("AI_API_KEY is missing in .env.")
        headers = {"Authorization": f"Bearer {key}"}
    else:
        base = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434").rstrip("/")
        model = os.getenv("OLLAMA_MODEL", "qwen2.5:7b")
        headers = {}
    payload = {"model": model, "messages": [{"role":"system","content":SYSTEM}, *messages], "stream": False}
    async with httpx.AsyncClient(timeout=120) as client:
        r = await client.post(base + "/v1/chat/completions", json=payload, headers=headers)
        r.raise_for_status()
        data = r.json()
    return data["choices"][0]["message"]["content"]

def list_files():
    return [str(p.relative_to(WORKSPACE)) for p in WORKSPACE.rglob("*") if p.is_file()][:200]

def read_file(name):
    p = safe_path(name)
    if not p.is_file(): raise FileNotFoundError(name)
    if p.stat().st_size > 1_000_000: raise ValueError("File exceeds 1 MB limit.")
    return p.read_text(encoding="utf-8")

def write_file(name, content):
    p = safe_path(name)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(content[:500_000], encoding="utf-8")
    return str(p.relative_to(WORKSPACE))

def run_python(name):
    p = safe_path(name)
    if not p.is_file() or p.suffix != ".py": raise ValueError("Choose an existing .py file in workspace.")
    result = subprocess.run([sys.executable, "-I", str(p)], cwd=str(WORKSPACE),
                            capture_output=True, text=True, timeout=10)
    return {"returncode": result.returncode, "stdout": result.stdout[-12000:], "stderr": result.stderr[-12000:]}

async def web_search(query):
    try:
        from ddgs import DDGS
        results = list(DDGS().text(query, max_results=5))
        return [{"title": x.get("title"), "url": x.get("href"), "snippet": x.get("body")} for x in results]
    except ImportError:
        raise RuntimeError("Optional search package missing. Run: pip install ddgs")
    except Exception as e:
        raise RuntimeError(f"Search unavailable: {e}")
