"""Thin client for Cerebras' OpenAI-compatible chat completions endpoint.
No SDK dependency — this is the only call site, so a raw httpx POST is simpler
than pulling in another package for one request shape.
"""
import httpx

from app.core.config import settings


class CerebrasError(Exception):
    pass


async def chat_completion(messages: list[dict], temperature: float = 0.3, max_tokens: int = 350) -> str:
    if not settings.cerebras_api_key:
        raise CerebrasError("CEREBRAS_API_KEY is not configured")

    async with httpx.AsyncClient(timeout=20.0) as client:
        try:
            resp = await client.post(
                f"{settings.cerebras_base_url}/chat/completions",
                headers={"Authorization": f"Bearer {settings.cerebras_api_key}"},
                json={
                    "model": settings.cerebras_model,
                    "messages": messages,
                    "temperature": temperature,
                    "max_tokens": max_tokens,
                },
            )
            resp.raise_for_status()
        except httpx.HTTPStatusError as exc:
            raise CerebrasError(f"Cerebras request failed ({exc.response.status_code}): {exc.response.text[:300]}")
        except httpx.HTTPError as exc:
            raise CerebrasError(f"Could not reach Cerebras: {exc}")

    data = resp.json()
    try:
        return data["choices"][0]["message"]["content"].strip()
    except (KeyError, IndexError):
        raise CerebrasError("Unexpected response shape from Cerebras")
