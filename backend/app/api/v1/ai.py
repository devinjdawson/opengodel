from typing import Any

import openai
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

from app.core.config import settings
from app.services.inference_service import inference_service, ChatMessage
from app.services.openbb_service import openbb_service

router = APIRouter(prefix="/ai", tags=["AI"])


def _inference_unavailable(exc: Exception) -> HTTPException:
    return HTTPException(
        status_code=503,
        detail=(
            f"Inference server unreachable at {settings.inference_base_url} "
            f"(model: {settings.inference_model}). Start the llama.cpp server "
            f"or update INFERENCE_BASE_URL. Original error: {exc}"
        ),
    )


_langfuse_client = None


def _get_langfuse():
    global _langfuse_client
    if _langfuse_client is None:
        if settings.langfuse_public_key and settings.langfuse_secret_key:
            from langfuse import Langfuse
            _langfuse_client = Langfuse(
                public_key=settings.langfuse_public_key,
                secret_key=settings.langfuse_secret_key,
                base_url=settings.langfuse_base_url,
            )
    return _langfuse_client


def _sanitize_for_langfuse(value: Any) -> Any:
    if isinstance(value, str):
        if "sk-" in value or "Bearer " in value:
            return "[REDACTED]"
        return value
    if isinstance(value, dict):
        return {k: _sanitize_for_langfuse(v) for k, v in value.items()}
    if isinstance(value, list):
        return [_sanitize_for_langfuse(item) for item in value]
    return value


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


# Financial Agent Models
class AgentChatRequest(BaseModel):
    message: str
    context: dict[str, Any] | None = None
    stream: bool = False


class AgentChatResponse(BaseModel):
    response: str
    widgets: list[str] | None = None
    data: dict[str, Any] | None = None


FINANCIAL_SYSTEM_PROMPT = """You are OG Terminal, an AI financial assistant with access to real-time market data, news, and analytics through the OpenBB Platform.

You can help users with:
- Stock quotes, charts, and technical analysis
- Fundamental data (financials, ratios, earnings)
- Macro economic indicators (yields, inflation, employment)
- News and sentiment analysis
- Options data (chains, Greeks, volatility surfaces)
- Portfolio analysis and risk metrics

When users ask for data, use the available tools to fetch real-time information. Provide clear, actionable insights with specific numbers and references.

Current context: {context}

Available widgets you can reference:
- equity: candlestick, technical_indicators, quote_summary
- macro: yield_curve, inflation_dashboard, fed_balance_sheet, employment_dashboard, macro_table
- news: latest_articles, semantic_search, sentiment_analysis, news_symbols
- options: volatility_surface, option_chain, iv_term_structure, greeks_dashboard
- portfolio: performance, allocation, correlation_matrix, risk_metrics
- og: AL, DES, FA, GR, ERN, INS, IMAPI, DVD

If a user's question maps to a widget, mention the widget endpoint they can add to their dashboard.""" 


@router.post("/chat", response_model=ChatResponse)
async def chat_completion(request: ChatRequest):
    """Non-streaming chat completion."""
    if request.stream:
        raise HTTPException(status_code=400, detail="Use /chat/stream for streaming responses")

    langfuse = _get_langfuse()
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
        response = ChatResponse(
            content=message.content or "",
            role=message.role,
            tool_calls=[tc.model_dump() for tc in message.tool_calls] if message.tool_calls else None,
        )

        if langfuse:
            try:
                with langfuse.start_as_current_observation(
                    as_type="span",
                    name="chat-completion",
                    input={
                        "messages": _sanitize_for_langfuse(request.messages),
                        "model": request.model,
                        "temperature": request.temperature,
                        "max_tokens": request.max_tokens,
                    },
                    metadata={"endpoint": "/ai/chat"},
                ):
                    with langfuse.start_as_current_observation(
                        as_type="generation",
                        name="chat-completion",
                        model=completion.model or settings.inference_model,
                        input=_sanitize_for_langfuse(request.messages),
                    ) as generation:
                        generation.update(
                            output=message.content or "",
                            usage_details={
                                "input_tokens": completion.usage.prompt_tokens if completion.usage else None,
                                "output_tokens": completion.usage.completion_tokens if completion.usage else None,
                                "total_tokens": completion.usage.total_tokens if completion.usage else None,
                            },
                        )
            except Exception:
                pass

        return response
    except openai.APIConnectionError as e:
        raise _inference_unavailable(e)
    except openai.AuthenticationError as e:
        raise HTTPException(
            status_code=503,
            detail=f"Inference server rejected the API key (INFERENCE_API_KEY/OPENAI_API_KEY): {e}",
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/health")
async def inference_health():
    """Probe the configured inference server (llama.cpp) for reachability."""
    import httpx

    base_url = (settings.inference_base_url or "").rstrip("/")
    if not base_url:
        raise HTTPException(status_code=503, detail="INFERENCE_BASE_URL is not configured")

    headers = {}
    api_key = settings.inference_api_key or settings.openai_api_key
    if api_key:
        headers["Authorization"] = f"Bearer {api_key}"

    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            resp = await client.get(f"{base_url}/models", headers=headers)
        models = []
        if resp.status_code == 200:
            try:
                data = resp.json()
                models = [m.get("name") or m.get("id") for m in data.get("models", data.get("data", [])) if isinstance(m, dict)]
            except Exception:
                pass
        return {
            "status": "ok" if resp.status_code == 200 else "error",
            "base_url": base_url,
            "model": settings.inference_model,
            "http_status": resp.status_code,
            "models": models,
        }
    except Exception as e:
        return {
            "status": "unreachable",
            "base_url": base_url,
            "model": settings.inference_model,
            "error": str(e),
        }


@router.post("/chat/stream")
async def chat_completion_stream(request: ChatRequest):
    """Streaming chat completion (SSE)."""
    request.stream = True

    langfuse = _get_langfuse()
    span = None
    generation = None
    if langfuse:
        span = langfuse.start_observation(
            as_type="span",
            name="chat-completion-stream",
            input={
                "messages": _sanitize_for_langfuse(request.messages),
                "model": request.model,
                "temperature": request.temperature,
                "max_tokens": request.max_tokens,
            },
            metadata={"endpoint": "/ai/chat/stream"},
        )
        generation = span.start_observation(
            as_type="generation",
            name="chat-completion-stream",
            model=request.model or settings.inference_model,
            input=_sanitize_for_langfuse(request.messages),
        )

    async def generate():
        accumulated = []
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
                    content = chunk.choices[0].delta.content
                    accumulated.append(content)
                    yield f"data: {content}\n\n"
            yield "data: [DONE]\n\n"
        except Exception as e:
            yield f"data: {{\"error\": \"{str(e)}\"}}\n\n"
        finally:
            if generation:
                generation.update(output="".join(accumulated))
                generation.end()
            if span:
                span.update(output={"response": "".join(accumulated)})
                span.end()

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


@router.post("/agent/chat", response_model=AgentChatResponse)
async def agent_chat(request: AgentChatRequest):
    """Financial agent chat endpoint with context awareness."""
    langfuse = _get_langfuse()
    try:
        # Build context-aware system prompt
        context_str = ""
        context_metadata = {}
        if request.context:
            symbol = request.context.get("symbol", "AAPL")
            context_str = f"Current symbol: {symbol}. "
            context_metadata = {"symbol": symbol}
            if "start_date" in request.context:
                context_str += f"Date range: {request.context['start_date']} to {request.context['end_date']}. "
                context_metadata["date_range"] = f"{request.context['start_date']} to {request.context['end_date']}"
        
        system_prompt = FINANCIAL_SYSTEM_PROMPT.format(context=context_str)
        
        messages = [
            ChatMessage(role="system", content=system_prompt),
            ChatMessage(role="user", content=request.message),
        ]
        
        # Add context from previous conversation if available
        # For now, single-turn conversation
        
        completion = await inference_service.chat_completion(
            messages=messages,
            temperature=0.3,
            max_tokens=2048,
            stream=False,
        )
        
        response_content = completion.choices[0].message.content or "I couldn't process that request."
        
        # Detect if response mentions specific widgets
        widget_keywords = {
            "candlestick": "candlestick",
            "technical": "technical_indicators",
            "quote": "quote_summary",
            "yield curve": "yield_curve",
            "inflation": "inflation_dashboard",
            "fed balance": "fed_balance_sheet",
            "employment": "employment_dashboard",
            "macro table": "macro_table",
            "news": "latest_articles",
            "sentiment": "sentiment_analysis",
            "options": "option_chain",
            "volatility": "volatility_surface",
            "greeks": "greeks_dashboard",
            "iv term": "iv_term_structure",
            "portfolio": "performance",
            "allocation": "allocation",
            "correlation": "correlation_matrix",
            "risk": "risk_metrics",
        }
        
        suggested_widgets = []
        response_lower = response_content.lower()
        for keyword, widget in widget_keywords.items():
            if keyword in response_lower:
                suggested_widgets.append(widget)
        
        agent_response = AgentChatResponse(
            response=response_content,
            widgets=suggested_widgets[:3] if suggested_widgets else None,
            data={"context_used": request.context},
        )

        if langfuse:
            try:
                with langfuse.start_as_current_observation(
                    as_type="span",
                    name="agent-chat",
                    input={
                        "message": _sanitize_for_langfuse(request.message),
                        "context": _sanitize_for_langfuse(request.context),
                    },
                    metadata={
                        "endpoint": "/ai/agent/chat",
                        **context_metadata,
                    },
                ):
                    with langfuse.start_as_current_observation(
                        as_type="generation",
                        name="agent-chat",
                        model=completion.model or settings.inference_model,
                        input=_sanitize_for_langfuse(messages),
                    ) as generation:
                        generation.update(
                            output=response_content,
                            usage_details={
                                "input_tokens": completion.usage.prompt_tokens if completion.usage else None,
                                "output_tokens": completion.usage.completion_tokens if completion.usage else None,
                                "total_tokens": completion.usage.total_tokens if completion.usage else None,
                            },
                            metadata={
                                "suggested_widgets": suggested_widgets[:3] if suggested_widgets else None,
                            },
                        )
            except Exception:
                pass

        return agent_response
    except openai.APIConnectionError as e:
        raise _inference_unavailable(e)
    except openai.AuthenticationError as e:
        raise HTTPException(
            status_code=503,
            detail=f"Inference server rejected the API key (INFERENCE_API_KEY/OPENAI_API_KEY): {e}",
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
