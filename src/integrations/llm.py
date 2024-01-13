
from openai import AsyncOpenAI
from typing import List, Optional


class ArticleChunk:
    def __init__(self, text: str, embeddings: List[float]) -> None:
        self.text = text
        self.embeddings = embeddings


class ChatCompletionMessage:
    def __init__(self, role: str, content: str) -> None:
        self.role = role
        self.content = content


class LLM:
    def __init__(self, client: AsyncOpenAI = AsyncOpenAI()) -> None:
        self.client = client

    async def get_response(self, messages: List[ChatCompletionMessage], model: str = "gpt-3.5-turbo-16k", response_format: dict[str, str] = {}) -> str:
        return await self.client.chat.completions.create(
            temperature=0,
            response_format=response_format,
            model=model,
            messages=[m.__dict__ for m in messages]
        )

    async def get_embedding(self, text: str, model="text-embedding-ada-002") -> Optional[str]:
        """
        Use openai embedding API to create embeddings for the document.
        """
        # print(f"FETCHING EMBEDDING FOR {text}...")
        return await self.client.embeddings.create(
            model=model,
            input=[text]
        )
