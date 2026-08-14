from typing import Any

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

from app.services.inference_service import inference_service, ChatMessage
from app.services.openbb_service import openbb_service

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


@router.post("/agent/chat", response_model=AgentChatResponse)
async def agent_chat(request: AgentChatRequest):
    """Financial agent chat endpoint with context awareness."""
    try:
        # Build context-aware system prompt
        context_str = ""
        if request.context:
            symbol = request.context.get("symbol", "AAPL")
            context_str = f"Current symbol: {symbol}. "
            if "start_date" in request.context:
                context_str += f"Date range: {request.context['start_date']} to {request.context['end_date']}. "
        
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
        
        return AgentChatResponse(
            response=response_content,
            widgets=suggested_widgets[:3] if suggested_widgets else None,
            data={"context_used": request.context},
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
