# Task 3: Intent-Based Natural Language Routing - Implementation Plan

## Overview

This task adds LLM-powered natural language understanding to the bot. Users can ask questions in plain English, and the bot will figure out which API calls to make and how to answer.

## Architecture

The intent router follows the tool-calling pattern from Lab 6:

```
User message → LLM (with tool definitions) → Tool calls → Execute API calls → 
Feed results to LLM → Final answer
```

### Components

1. **LLM Client** (`services/llm_client.py`)
   - Wraps the Qwen Code API (or any OpenAI-compatible API)
   - Supports tool/function calling
   - Handles the conversation loop with tool feedback

2. **Tool Definitions** (`services/tools.py`)
   - Defines all 9 backend endpoints as tool schemas
   - Each tool has: name, description, parameters
   - Tool descriptions must be clear so LLM knows when to use each

3. **Intent Router** (`handlers/intent_router.py`)
   - Takes user message
   - Calls LLM with tools
   - Executes tool calls
   - Feeds results back
   - Returns final answer

4. **Updated Entry Point** (`bot.py`)
   - Routes non-slash messages to intent router
   - Slash commands still use regular handlers
   - Debug logging to stderr for tool call tracing

## Implementation Steps

### Step 1: Create LLM Client
- Use httpx for async HTTP calls
- Support OpenAI-compatible API format
- Implement tool calling loop
- Handle errors gracefully

### Step 2: Define Tool Schemas
- All 9 backend endpoints as tools
- Clear, specific descriptions
- Proper parameter schemas

### Step 3: Implement Intent Router
- Single-step queries (one tool call)
- Multi-step queries (multiple tool calls with feedback)
- Fallback for greetings and gibberish

### Step 4: Add Inline Keyboard Buttons
- Show after /start command
- Common actions: "List labs", "Check health", "Show scores"

### Step 5: Update bot.py
- Route plain text to intent router
- Keep slash commands working
- Add debug logging

### Step 6: Test Thoroughly
- Single-step queries
- Multi-step queries
- Edge cases (gibberish, greetings)
- Error handling (LLM down, backend down)

## Testing Strategy

Test mode with debug output:
```
uv run bot.py --test "what labs are available"
# stderr: [tool] LLM called: get_items({})
# stderr: [tool] Result: 44 items
# stdout: There are 6 main labs available...
```

## Dependencies

Add to pyproject.toml:
- Already have: httpx, python-dotenv
- No new dependencies needed (using existing httpx)

## Risks

1. **LLM token expiration** - Qwen OAuth tokens expire. Document restart procedure.
2. **Tool descriptions unclear** - LLM won't call right tools. Iterate on descriptions.
3. **Tool results not fed back** - Multi-step queries fail. Verify conversation loop.

## Acceptance Criteria Checklist

- [ ] --test "what labs are available" returns 20+ chars
- [ ] --test "which lab has the lowest pass rate" names a lab
- [ ] --test "asdfgh" returns helpful message
- [ ] Keyboard buttons implemented
- [ ] 9+ tool schemas defined
- [ ] LLM decides tool calls (no regex routing)
- [ ] Tool results fed back to LLM
