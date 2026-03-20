# Task 4: Containerize and Deploy - Implementation Plan

## Overview

This task containerizes the bot and deploys it alongside the backend as a Docker service. The bot will restart automatically, logs will be managed by Docker, and it will run in production properly.

## Deliverables

### 1. Bot Dockerfile (`bot/Dockerfile`)

**Approach:**
- Use Python 3.12 slim base image
- Install uv for dependency management
- Copy pyproject.toml and uv.lock first (layer caching)
- Run `uv sync --frozen` to install dependencies
- Copy bot source code
- Set entry point to run bot.py

**Key considerations:**
- No requirements.txt - use uv and pyproject.toml only
- Copy uv.lock to ensure reproducible builds
- Working directory: /app
- Non-root user for security (optional but recommended)

### 2. Docker Compose Service

**Add to existing `docker-compose.yml`:**

```yaml
bot:
  build:
    context: ./bot
    dockerfile: Dockerfile
  environment:
    - BOT_TOKEN=${BOT_TOKEN:?'BOT_TOKEN is required'}
    - LMS_API_URL=http://backend:8000
    - LMS_API_KEY=${LMS_API_KEY:?'LMS_API_KEY is required'}
    - LLM_API_KEY=${LLM_API_KEY:?'LLM_API_KEY is required'}
    - LLM_API_BASE_URL=http://host.docker.internal:42005/v1
    - LLM_API_MODEL=${LLM_API_MODEL:-coder-model}
  extra_hosts:
    - "host.docker.internal:host-gateway"
  depends_on:
    - backend
  restart: unless-stopped
  networks:
    - se-toolkit-network
```

**Key networking changes:**
- `LMS_API_URL` changes from `http://localhost:42002` to `http://backend:8000`
- `LLM_API_BASE_URL` uses `host.docker.internal` to reach the Qwen proxy
- `extra_hosts` enables host.docker.internal on Linux

### 3. Environment Configuration

**Update `.env.docker.secret`:**
- Add BOT_TOKEN
- Add LLM_API_KEY, LLM_API_BASE_URL, LLM_API_MODEL
- Ensure LMS_API_URL and LMS_API_KEY are set

**Update `.env.bot.example`:**
- Document all required fields for reference

### 4. README Deployment Documentation

**Add "Deploy" section with:**
- Prerequisites (VM, Docker, Qwen proxy)
- Environment setup (.env.docker.secret)
- Deploy commands (docker compose up)
- Verify commands (docker ps, logs, Telegram test)
- Troubleshooting tips

## Implementation Steps

1. Create `bot/Dockerfile`
2. Update `.env.docker.secret` with bot credentials
3. Add bot service to `docker-compose.yml`
4. Add README deploy section
5. Test locally (docker compose up)
6. Deploy to VM
7. Verify in Telegram

## Testing Strategy

1. **Build test:** `docker compose build bot` succeeds
2. **Startup test:** Container starts without errors
3. **Functionality test:** All commands work from container
4. **Network test:** Bot can reach backend and LLM proxy

## Risks

1. **Docker networking:** Bot can't reach backend or LLM proxy
   - Mitigation: Use service names and host.docker.internal
2. **Environment variables:** Missing credentials in container
   - Mitigation: Validate required env vars in compose file
3. **Build failures:** uv.lock out of sync
   - Mitigation: Run uv lock before building

## Acceptance Criteria Checklist

- [ ] bot/Dockerfile exists
- [ ] docker-compose.yml has bot service
- [ ] Bot container running (docker ps)
- [ ] Backend still healthy (curl returns 200)
- [ ] README has deploy section
- [ ] Bot responds in Telegram from container
- [ ] Git workflow followed
