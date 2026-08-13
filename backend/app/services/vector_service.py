from typing import Any

import openai
from sentence_transformers import SentenceTransformer
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.db.models import NewsArticle


class VectorService:
    def __init__(self):
        self._local_model: SentenceTransformer | None = None
        self._openai_client: openai.AsyncOpenAI | None = None
        self._embedding_client: openai.AsyncOpenAI | None = None

    def _get_local_model(self) -> SentenceTransformer:
        if self._local_model is None:
            self._local_model = SentenceTransformer("all-MiniLM-L6-v2")
        return self._local_model

    def _get_openai_client(self) -> openai.AsyncOpenAI:
        if self._openai_client is None:
            api_key = (
                settings.inference_api_key
                or settings.openai_api_key
            )
            base_url = settings.inference_base_url
            self._openai_client = openai.AsyncOpenAI(
                api_key=api_key,
                base_url=base_url,
            )
        return self._openai_client

    def _get_embedding_client(self) -> openai.AsyncOpenAI:
        if self._embedding_client is None:
            api_key = (
                settings.embedding_api_key
                or settings.inference_api_key
                or settings.openai_api_key
            )
            base_url = settings.embedding_base_url or settings.inference_base_url
            self._embedding_client = openai.AsyncOpenAI(
                api_key=api_key,
                base_url=base_url,
            )
        return self._embedding_client

    def _should_use_openai(self) -> bool:
        provider = settings.embedding_provider.lower()
        return provider in ("openai", "azure", "openrouter", "ollama", "deepseek", "groq", "together", "fireworks", "cohere", "voyage", "jina", "mixedbread")

    async def generate_embedding(self, text: str) -> list[float]:
        if self._should_use_openai():
            return await self._generate_openai_compatible_embedding(text)
        return await self._generate_local_embedding(text)

    async def _generate_openai_compatible_embedding(self, text: str) -> list[float]:
        client = self._get_embedding_client()
        response = await client.embeddings.create(
            model=settings.embedding_model,
            input=text,
            dimensions=settings.embedding_dimensions,
        )
        return response.data[0].embedding

    async def _generate_local_embedding(self, text: str) -> list[float]:
        model = self._get_local_model()
        embedding = model.encode(text, normalize_embeddings=True)
        return embedding.tolist()

    async def search_similar_news(
        self,
        db: AsyncSession,
        query: str,
        limit: int = 10,
        symbol: str | None = None,
    ) -> list[NewsArticle]:
        query_vector = await self.generate_embedding(query)

        stmt = (
            select(NewsArticle)
            .order_by(NewsArticle.embedding.cosine_distance(query_vector))
            .limit(limit)
        )

        if symbol:
            stmt = stmt.where(NewsArticle.symbol == symbol)

        result = await db.execute(stmt)
        return result.scalars().all()

    async def store_news_with_embedding(
        self,
        db: AsyncSession,
        articles: list[dict],
    ) -> list[NewsArticle]:
        stored = []
        for article in articles:
            embedding = await self.generate_embedding(
                f"{article['title']} {article['content']}"
            )

            news = NewsArticle(
                id=article.get("id"),
                symbol=article.get("symbol", ""),
                title=article["title"],
                content=article["content"],
                source=article["source"],
                url=article["url"],
                published_at=article["published_at"],
                embedding=embedding,
            )
            db.add(news)
            stored.append(news)

        await db.commit()
        for news in stored:
            await db.refresh(news)
        return stored


vector_service = VectorService()