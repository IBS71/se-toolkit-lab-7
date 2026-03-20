"""
LLM Client - Handles tool calling with Qwen Code API (OpenAI-compatible).

Usage:
    from services import LLMClient
    client = LLMClient(api_key, base_url, model)
    response = await client.chat_with_tools(messages, tools)
"""

import httpx
from typing import Any, Optional
import json


class LLMClient:
    """Client for LLM with tool calling support."""

    def __init__(self, api_key: str, base_url: str, model: str):
        self.api_key = api_key
        self.base_url = base_url.rstrip("/")
        self.model = model
        self._client: Optional[httpx.AsyncClient] = None

    async def _get_client(self) -> httpx.AsyncClient:
        """Get or create the HTTP client with auth headers."""
        if self._client is None or self._client.is_closed:
            self._client = httpx.AsyncClient(
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json",
                },
                timeout=30.0,
            )
        return self._client

    async def close(self):
        """Close the HTTP client."""
        if self._client and not self._client.is_closed:
            await self._client.aclose()

    async def chat_with_tools(
        self,
        messages: list[dict[str, Any]],
        tools: list[dict[str, Any]],
        max_iterations: int = 5,
    ) -> str:
        """
        Chat with the LLM using tool calling.

        Args:
            messages: Conversation history with role/content format
            tools: List of tool schemas
            max_iterations: Maximum tool call iterations before giving up

        Returns:
            Final response from the LLM
        """
        client = await self._get_client()

        for iteration in range(max_iterations):
            # Call the LLM
            response = await client.post(
                f"{self.base_url}/chat/completions",
                json={
                    "model": self.model,
                    "messages": messages,
                    "tools": tools,
                    "tool_choice": "auto",
                },
            )
            response.raise_for_status()
            data = response.json()

            if not data.get("choices"):
                return "LLM returned no response."

            choice = data["choices"][0]
            message = choice.get("message", {})

            # Check if LLM wants to call tools
            tool_calls = message.get("tool_calls", [])

            if not tool_calls:
                # No tool calls - return the final response
                return message.get("content", "No response generated.")

            # Add the assistant's message with tool calls to conversation
            messages.append(message)

            # Execute each tool call
            for tool_call in tool_calls:
                function = tool_call.get("function", {})
                tool_name = function.get("name", "")
                tool_args_str = function.get("arguments", "{}")

                try:
                    tool_args = json.loads(tool_args_str) if tool_args_str else {}
                except json.JSONDecodeError:
                    tool_args = {}

                # Execute the tool
                result = await self._execute_tool(tool_name, tool_args)

                # Add tool result to conversation
                messages.append(
                    {
                        "role": "tool",
                        "tool_call_id": tool_call.get("id", ""),
                        "content": json.dumps(result) if isinstance(result, dict) else str(result),
                    }
                )

                # Debug output to stderr
                print(f"[tool] LLM called: {tool_name}({tool_args})", file=__import__("sys").stderr)
                print(f"[tool] Result: {str(result)[:100]}...", file=__import__("sys").stderr)

            print(f"[summary] Feeding {len(tool_calls)} tool result(s) back to LLM", file=__import__("sys").stderr)

        return "Reached maximum iterations. Please try rephrasing your question."

    async def _execute_tool(self, name: str, arguments: dict[str, Any]) -> Any:
        """Execute a tool by calling the appropriate method."""
        from config import load_config

        config = load_config()
        base_url = config.get("LMS_API_URL", "http://localhost:42002")
        api_key = config.get("LMS_API_KEY", "")

        # Create LMS client for backend calls
        from services import LMSClient

        lms = LMSClient(base_url, api_key)

        try:
            if name == "get_items":
                return await lms.get_items()
            elif name == "get_learners":
                return await lms.get_learners()
            elif name == "get_scores":
                return await lms.get_analytics("scores", lab=arguments.get("lab"))
            elif name == "get_pass_rates":
                return await lms.get_analytics("pass-rates", lab=arguments.get("lab"))
            elif name == "get_timeline":
                return await lms.get_analytics("timeline", lab=arguments.get("lab"))
            elif name == "get_groups":
                return await lms.get_analytics("groups", lab=arguments.get("lab"))
            elif name == "get_top_learners":
                return await lms.get_analytics(
                    "top-learners",
                    lab=arguments.get("lab"),
                    limit=arguments.get("limit", 5),
                )
            elif name == "get_completion_rate":
                return await lms.get_analytics("completion-rate", lab=arguments.get("lab"))
            elif name == "trigger_sync":
                client = await lms._get_client()
                resp = await client.post(f"{base_url}/pipeline/sync")
                resp.raise_for_status()
                return resp.json()
            else:
                return {"error": f"Unknown tool: {name}"}
        except Exception as e:
            return {"error": str(e)}
        finally:
            await lms.close()
