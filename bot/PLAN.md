# Bot Development Plan

## Overview

This document outlines the development plan for the LMS Telegram bot across four tasks. The bot allows users to interact with the LMS backend through Telegram chat, supporting both slash commands and natural language queries.

## Architecture

The bot follows a **layered architecture** with clear separation of concerns:

1. **Entry Point** (`bot.py`) — Handles Telegram connection and `--test` mode
2. **Handlers** (`handlers/`) — Pure functions that process commands and return responses
3. **Services** (`services/`) — External API clients (LMS backend, LLM)
4. **Config** (`config.py`) — Environment variable loading

This architecture enables **testable handlers**: the same handler functions work in `--test` mode, unit tests, and the live Telegram bot.

---

## Task 1: Plan and Scaffold

**Goal:** Create project structure and test mode.

**Approach:**
- Scaffold the `bot/` directory with `pyproject.toml` for dependencies
- Create handler modules as pure functions (no Telegram dependency)
- Implement `--test` mode that calls handlers directly and prints to stdout
- Create `config.py` for loading `.env.bot.secret`

**Why this matters:** Test mode allows rapid iteration without deploying to Telegram. Handlers can be tested in isolation.

---

## Task 2: Backend Integration

**Goal:** Connect handlers to the real LMS backend.

**Approach:**
- Create `services/lms_client.py` — HTTP client for backend API calls
- Implement Bearer token authentication using `LMS_API_KEY`
- Update handlers to call the API:
  - `/health` → `GET /health` → report up/down status
  - `/labs` → `GET /items?type=lab` → list labs
  - `/scores <lab>` → `GET /analytics/<lab_id>` → show pass rates
- Add error handling for network failures and API errors

**Why this matters:** Users can now check system health and browse labs through Telegram.

---

## Task 3: Intent-Based Natural Language Routing

**Goal:** Enable plain text queries using LLM tool use.

**Approach:**
- Create `services/llm_client.py` — LLM client for tool calling
- Wrap each backend endpoint as an LLM tool with clear descriptions
- Implement intent router: user message → LLM → tool selection → API call → response
- Focus on tool description quality — the LLM reads these to decide which tool to call
- Add inline keyboard buttons for common actions (quick replies)

**Why this matters:** Users can ask questions naturally like "What labs are due soon?" instead of memorizing commands.

---

## Task 4: Containerize and Deploy

**Goal:** Deploy the bot alongside the backend on the VM.

**Approach:**
- Create `bot/Dockerfile` — minimal Python image with bot dependencies
- Add bot service to `docker-compose.yml`
- Configure Docker networking: bot uses service name `backend` instead of `localhost`
- Set up health checks and restart policies
- Document deployment in README

**Why this matters:** The bot runs 24/7 on the VM, accessible to all users via Telegram.

---

## Testing Strategy

1. **Test mode** — `uv run bot.py --test "/command"` for quick iteration
2. **Unit tests** — Test handlers in isolation (future enhancement)
3. **Manual Telegram testing** — Deploy and test in real Telegram chats
4. **Autochecker verification** — Automated checks for all acceptance criteria

---

## Risk Mitigation

- **Backend down:** Handlers return friendly error messages, not crashes
- **LLM unavailable:** Fallback to slash commands only
- **Token limits:** Cache responses where appropriate
- **Secrets exposure:** `.env.bot.secret` is gitignored, never commit
