# prompty-prototype

A prototype [Model Context Protocol](https://modelcontextprotocol.io/) server that rewrites a rough prompt into a clearer one before it reaches the model.

The rewriting is rule-based, with no LLM call: it checks the prompt for vagueness, missing context and a missing action verb, then adds a role, format requirements and constraints where they help. The guidelines it follows live in `improvement_prompt.md`.

## What's in here

| File | What it is |
| --- | --- |
| `main.py` | MCP server over stdio with one tool, `improve_prompt` |
| `auto_improve_main.py` | Variant that adds a tool meant to run on every user message |
| `server.py` | The same logic as a FastAPI HTTP endpoint, `POST /improve-prompt` |
| `improvement_prompt.md` | The prompt-improvement guidelines |

## Setup

Python 3.12 or newer.

```bash
pip install -r requirements.txt
```

### As an MCP server

Copy `claude_config.example.json` into your MCP client's config, set `cwd` to where you cloned this repo, and restart the client. The `improve_prompt` tool takes a `user_prompt` and an optional `context`.

### As an HTTP server

```bash
python server.py   # http://127.0.0.1:8000
```

## Status

A prototype from July 2025. It works, but the heuristics are deliberately simple.
