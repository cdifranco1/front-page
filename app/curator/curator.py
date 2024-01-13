import json
from .prompts import ArticlePrompts
from .llm import LLM, ChatCompletionMessage
from .scraper import Scraper
from src.repository.model import EmbeddingDocument, CanonicalDocument
from typing import List, Optional
from asyncio import TaskGroup
from langchain.text_splitter import RecursiveCharacterTextSplitter
import uuid


class UrlDocs:
    def __init__(self, canonical_doc: CanonicalDocument, embedding_docs: List[EmbeddingDocument]) -> None:
        self.canonical_doc = canonical_doc
        self.embedding_docs = embedding_docs


class Curator:
    def __init__(self, scraper: Scraper, llm: LLM) -> None:
        self.llm = llm
        self.scraper = scraper

    async def get_single_article_documents(self, url: str) -> UrlDocs:
        """
        Return UrlDocs object with a single canonical document and a list of embedding documents.
        """
        print(f"Scraping {url}...")
        url_content = await self.scraper.scrape_content(url)

        canonical_id = str(uuid.uuid5(uuid.NAMESPACE_URL, url))
        canonical_doc = CanonicalDocument(id=canonical_id, url=url)

        async with TaskGroup() as embedding_task_group:
            results = []
            for chunk in self._chunk_text(url_content):
                results.append(embedding_task_group.create_task(
                    self.create_embedding_doc(canonical_id=canonical_id, text=chunk)))

        print(f"Created {len(results)} embedding documents")
        return UrlDocs(canonical_doc=canonical_doc, embedding_docs=[r.result() for r in results])

    async def gather_article_summaries(self, url: str, limit: int = 1) -> List[dict[str, str]]:
        article_links = await self.scraper.scrape_site(url)

        async with TaskGroup() as summary_task_group:
            results = []
            for link in article_links[:limit]:
                results.append(summary_task_group.create_task(
                    self.summarize_article(link)))

        return [r.result() for r in results]

    async def gather_article_embeddings(self, url: str, limit: int = 1) -> List[UrlDocs]:
        article_links = await self.scraper.scrape_site(url)

        async with TaskGroup() as embeddings_task_group:
            results = []
            for link in article_links[:limit]:
                results.append(embeddings_task_group.create_task(
                    self.retrieve_article_embeddings(link)))

        return [r.result() for r in results]

    def _chunk_text(self, text: str, chunk_length: int = 1000, chunk_overlap: int = 100) -> List[str]:
        splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_length, chunk_overlap=chunk_overlap, length_function=len)

        return splitter.split_text(text)

    async def retrieve_article_embeddings(self, url: str, limit: int = 1) -> List[UrlDocs]:
        content = await self.scraper.scrape_content(url)
        chunks = self._chunk_text(content)

        canonical_doc = CanonicalDocument(url=url, content=content)

        async with TaskGroup() as summary_task_group:
            results = []
            for chunk in chunks:
                results.append(summary_task_group.create_task(
                    self.create_embedding_doc(url, chunk)))

        return UrlDocs(canonical_doc=canonical_doc, embedding_docs=[r.result() for r in results])

    async def create_embedding_doc(self, canonical_id: str, text: str) -> EmbeddingDocument:
        embedding_response = await self.llm.get_embedding(text)
        embedding_doc_id = str(uuid.uuid4())

        embedding_doc = EmbeddingDocument(
            id=embedding_doc_id, canonical_doc_id=canonical_id, content=text, embeddings=embedding_response.data[0].embedding)

        return embedding_doc

    async def _summarize(self, html_content: str) -> str:
        """
        Pass to the llm, and return the response
        """
        system_message = ChatCompletionMessage(
            role="system",
            content=ArticlePrompts.ARTICLE_SUMMARIZER_SYSTEM_PROMPT
        )
        user_message = ChatCompletionMessage(
            role="user",
            content=ArticlePrompts.ARTICLE_SUMMARIZER_USER_PROMPT.format(
                html=html_content)
        )
        chat_completion = await self.llm.get_response([system_message, user_message])
        response_json = json.loads(chat_completion.choices[0].message.content)
        return response_json

    async def summarize_article(self, link: str) -> Optional[str]:
        html = await self.scraper.ascrape_playwright(link)
        print("Summarizing article...")
        return await self._summarize(html)


if __name__ == "__main__":
    llm = LLM()
    scraper = Scraper()
    curator = Curator(scraper=scraper, llm=llm)
    import asyncio

    summaries = asyncio.run(curator.gather_article_summaries(
        "https://paulgraham.com"))

    # embeddings = asyncio.run(curator.retrieve_article_embeddings(
    #     "https://blog.colinbreck.com/"))

    # for e in embeddings:
    #     print(e)

    for s in summaries:
        print(s)
