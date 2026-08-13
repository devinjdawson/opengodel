from typing import Any

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

from app.services.inference_service import inference_service, ChatMessage

router = APIRouter(prefix="/ai", tags=["AI"])


class ChatRequest(BaseModel):
    messages: list[ChatMessage]
    model: str | None = None
    temperature: float | None = None
    max_tokens: int | None = None
    stream: bool = True
    tools: list[dict[str, Any]] | None = None
    tool_choice: str | dict[str, Any] | None = None


class ChatResponse(BaseModel):
    content: str
    role: str = "assistant"
    tool_calls: list[dict[str, Any]] | None = None


@router.post("/chat", response_model=ChatResponse)
async def chat_completion(request: ChatRequest):
    """Non-streaming chat completion."""
    if request.stream:
        raise HTTPException(status_code=400, detail="Use /chat/stream for streaming responses")

    try:
        completion = await inference_service.chat_completion(
            messages=request.messages,
            model=request.model,
            temperature=request.temperature,
            max_tokens=request.max_tokens,
            stream=False,
            tools=request.tools,
            tool_choice=request.tool_choice,
        )
        message = completion.choices[0].message
        return ChatResponse(
            content=message.content or "",
            role=message.role,
            tool_calls=[tc.model_dump() for tc in message.tool_calls] if message.tool_calls else None,
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/chat/stream")
async def chat_completion_stream(request: ChatRequest):
    """Streaming chat completion (SSE)."""
    request.stream = True

    async def generate():
        try:
            async for chunk in inference_service.chat_completion_stream(
                messages=request.messages,
                model=request.model,
                temperature=request.temperature,
                max_tokens=request.max_tokens,
                tools=request.tools,
                tool_choice=request.tool_choice,
            ):
                if chunk.choices and chunk.choices[0].delta.content:
                    yield f"data: {chunk.choices[0].delta.content}\n\n"
            yield "data: [DONE]\n\n"
        except Exception as e:
            yield f"data: {{\"error\": \"{str(e)}\"}}\n\n"

    return StreamingResponse(
        generate(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )


@router.get("/models")
async def list_models():
    """List available inference models (placeholder - extend with actual model registry)."""
    return {
        "inference": {
            "provider": "configurable",
            "model": "configurable",
            "base_url": "configurable",
        },
        "embedding": {
            "provider": "configurable",
            "model": "configurable",
            "base_url": "configurable",
        },
    }