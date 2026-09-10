"""Thin client for the assistant's OpenAI-compatible chat completions provider
(currently Groq). No SDK dependency — this is the only call site, so a raw
httpx POST is simpler than pulling in a package for one request shape.
Swapping providers only requires changing LLM_API_KEY/LLM_BASE_URL/LLM_MODEL.
"""
import httpx

from app.core.config import settings


class LLMError(Exception):
    pass


async def chat_completion(messages: list[dict], temperature: float = 0.3, max_tokens: int = 350) -> str:
    if not settings.llm_api_key:
        raise LLMError("LLM_API_KEY is not configured")

    async with httpx.AsyncClient(timeout=20.0) as client:
        try:
            resp = await client.post(
                f"{settings.llm_base_url}/chat/completions",
                headers={"Authorization": f"Bearer {settings.llm_api_key}"},
                json={
                    "model": settings.llm_model,
                    "messages": messages,
                    "temperature": temperature,
                    "max_tokens": max_tokens,
                },
            )
            resp.raise_for_status()
        except httpx.HTTPStatusError as exc:
            raise LLMError(f"LLM request failed ({exc.response.status_code}): {exc.response.text[:300]}")
        except httpx.HTTPError as exc:
            raise LLMError(f"Could not reach the LLM provider: {exc}")

    data = resp.json()
    try:
        # Some providers (e.g. gpt-oss reasoning models) include a separate
        # "reasoning" field alongside "content" — content is already the
        # clean final answer, so no extra parsing is needed here.
        return data["choices"][0]["message"]["content"].strip()
    except (KeyError, IndexError):
        raise LLMError("Unexpected response shape from LLM provider")
