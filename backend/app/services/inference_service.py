from typing import Any

import openai
from pydantic import BaseModel

from app.core.config import settings


class ChatMessage(BaseModel):
    role: str
    content: str


class InferenceService:
    def __init__(self):
        self._client: openai.AsyncOpenAI | None = None

    def _get_client(self) -> openai.AsyncOpenAI:
        if self._client is None:
            api_key = settings.inference_api_key or settings.openai_api_key
            base_url = settings.inference_base_url
            self._client = openai.AsyncOpenAI(
                api_key=api_key,
                base_url=base_url,
            )
        return self._client

    async def chat_completion(
        self,
        messages: list[ChatMessage],
        model: str | None = None,
        temperature: float | None = None,
        max_tokens: int | None = None,
        stream: bool = False,
        tools: list[dict[str, Any]] | None = None,
        tool_choice: str | dict[str, Any] | None = None,
    ):
        client = self._get_client()
        return await client.chat.completions.create(
            model=model or settings.inference_model,
            messages=[m.model_dump() for m in messages],
            temperature=temperature if temperature is not None else settings.inference_temperature,
            max_tokens=max_tokens or settings.inference_max_tokens,
            stream=stream,
            tools=tools,
            tool_choice=tool_choice,
        )

    async def chat_completion_stream(
        self,
        messages: list[ChatMessage],
        model: str | None = None,
        temperature: float | None = None,
        max_tokens: int | None = None,
        tools: list[dict[str, Any]] | None = None,
        tool_choice: str | dict[str, Any] | None = None,
    ):
        client = self._get_client()
        stream = await client.chat.completions.create(
            model=model or settings.inference_model,
            messages=[m.model_dump() for m in messages],
            temperature=temperature if temperature is not None else settings.inference_temperature,
            max_tokens=max_tokens or settings.inference_max_tokens,
            stream=True,
            tools=tools,
            tool_choice=tool_choice,
        )
        async for chunk in stream:
            yield chunk


inference_service = InferenceService()