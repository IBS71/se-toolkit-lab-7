# Lab 7 — Build a Client with an AI Coding Agent

[Sync your fork](https://docs.github.com/en/pull-requests/collaborating-with-pull-requests/working-with-forks/syncing-a-fork#syncing-a-fork-branch-from-the-command-line) regularly — the lab gets updated.

## Product brief

> Build a Telegram bot that lets users interact with the LMS backend through chat. Users should be able to check system health, browse labs and scores, and ask questions in plain language. The bot should use an LLM to understand what the user wants and fetch the right data. Deploy it alongside the existing backend on the VM.

This is what a customer might tell you. Your job is to turn it into a working product using an AI coding agent (Qwen Code) as your development partner.

```
┌──────────────────────────────────────────────────────────────┐
│                                                              │
│  ┌──────────────┐     ┌──────────────────────────────────┐   │
│  │  Telegram    │────▶│  Your Bot                        │   │
│  │  User        │◀────│  (aiogram / python-telegram-bot) │   │
│  └──────────────┘     └──────┬───────────────────────────┘   │
│                              │                               │
│                              │ slash commands + plain text    │
│                              ├───────▶ /start, /help         │
│                              ├───────▶ /health, /labs        │
│                              ├───────▶ intent router ──▶ LLM │
│                              │                    │          │
│                              │                    ▼          │
│  ┌──────────────┐     ┌──────┴───────┐    tools/actions      │
│  │  Docker      │     │  LMS Backend │◀───── GET /items      │
│  │  Compose     │     │  (FastAPI)   │◀───── GET /analytics  │
│  │              │     │  + PostgreSQL│◀───── POST /sync      │
│  └──────────────┘     └──────────────┘                       │
└──────────────────────────────────────────────────────────────┘
```

## Requirements

### P0 — Must have

1. Testable handler architecture — handlers work without Telegram
2. CLI test mode: `cd bot && uv run bot.py --test "/command"` prints response to stdout
3. `/start` — welcome message
4. `/help` — lists all available commands
5. `/health` — calls backend, reports up/down status
6. `/labs` — lists available labs
7. `/scores <lab>` — per-task pass rates
8. Error handling — backend down produces a friendly message, not a crash

### P1 — Should have

1. Natural language intent routing — plain text interpreted by LLM
2. All 9 backend endpoints wrapped as LLM tools
3. Inline keyboard buttons for common actions
4. Multi-step reasoning (LLM chains multiple API calls)

### P2 — Nice to have

1. Rich formatting (tables, charts as images)
2. Response caching
3. Conversation context (multi-turn)

### P3 — Deployment

1. Bot containerized with Dockerfile
2. Added as service in `docker-compose.yml`
3. Deployed and running on VM
4. README documents deployment

## Learning advice

Notice the progression above: **product brief** (vague customer ask) → **prioritized requirements** (structured) → **task specifications** (precise deliverables + acceptance criteria). This is how engineering work flows.

You are not following step-by-step instructions — you are building a product with an AI coding agent. The learning comes from planning, building, testing, and debugging iteratively.

## Learning outcomes

By the end of this lab, you should be able to say:

1. I turned a vague product brief into a working Telegram bot.
2. I can ask it questions in plain language and it fetches the right data.
3. I used an AI coding agent to plan and build the whole thing.

## Tasks

### Prerequisites

1. Complete the [lab setup](./lab/setup/setup-simple.md#lab-setup)

> **Note**: First time in this course? Do the [full setup](./lab/setup/setup-full.md#lab-setup) instead.

### Required

1. [Plan and Scaffold](./lab/tasks/required/task-1.md) — P0: project structure + `--test` mode
2. [Backend Integration](./lab/tasks/required/task-2.md) — P0: slash commands + real data
3. [Intent-Based Natural Language Routing](./lab/tasks/required/task-3.md) — P1: LLM tool use
4. [Containerize and Document](./lab/tasks/required/task-4.md) — P3: containerize + deploy

## Deploy

After completing all tasks, deploy the bot to your VM using Docker Compose.

### Prerequisites

- VM with Docker installed
- Backend running on VM (see [lab setup](./lab/setup/setup-simple.md#lab-setup))
- Qwen Code API proxy running on VM (port 42005)
- Telegram bot token from @BotFather

### Environment Setup

On your VM, edit `.env.docker.secret` and ensure these are set:

```bash
# Bot credentials
BOT_TOKEN=your-telegram-bot-token-from-botfather
LMS_API_KEY=your-lms-api-key
LLM_API_KEY=your-qwen-api-key
LLM_API_MODEL=coder-model
```

### Deploy Commands

```bash
# SSH to your VM
ssh root@YOUR_VM_IP

# Navigate to the project
cd ~/se-toolkit-lab-7

# Stop any running bot process (from Task 2-3)
pkill -f "bot.py" 2>/dev/null

# Build and start all services (including the bot)
docker compose --env-file .env.docker.secret up --build -d

# Verify all services are running
docker compose --env-file .env.docker.secret ps
```

You should see the `bot` service running alongside `backend`, `postgres`, `caddy`, and `pgadmin`.

### Verify Deployment

```bash
# Check bot logs
docker compose --env-file .env.docker.secret logs bot --tail 20

# Verify backend is still healthy
curl -sf http://localhost:42002/docs
```

### Test in Telegram

1. Open Telegram and find your bot (e.g., @your_bot_name)
2. Send `/start` — should receive welcome message
3. Send `/health` — should show backend status
4. Send "what labs are available?" — should list labs from backend
5. Send "show me scores for lab 4" — should show score data

### Troubleshooting

| Problem | Solution |
|---------|----------|
| Bot container keeps restarting | Check logs: `docker compose logs bot` |
| LLM queries fail | Ensure Qwen proxy is running: `curl http://localhost:42005/v1/models` |
| Backend connection refused | Verify `LMS_API_URL=http://backend:8000` in compose file |
| BOT_TOKEN error | Check `.env.docker.secret` has valid token |

### Undeploy (if needed)

```bash
# Stop bot only
docker compose --env-file .env.docker.secret stop bot

# Stop everything
docker compose --env-file .env.docker.secret down
```
