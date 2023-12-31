import json
from .prompts import ArticlePrompts
from .llm import LLM, ChatCompletionMessage
from .scraper import Scraper
from typing import List, Optional
from asyncio import TaskGroup
from langchain.text_splitter import RecursiveCharacterTextSplitter


class Curator:
    def __init__(self, scraper: Scraper, llm: LLM) -> None:
        self.llm = llm
        self.scraper = scraper

    async def is_full_article(self, html_content: str) -> bool:
        system_message = ChatCompletionMessage(
            role="system",
            content=ArticlePrompts.ARTICLE_CLASSIFIER_SYSTEM_PROMPT
        )
        user_message = ChatCompletionMessage(
            role="user",
            content=ArticlePrompts.ARTICLE_CLASSIFIER_USER_PROMPT.format(
                html=html_content)
        )
        chat_completion = self.llm.get_response([system_message, user_message])
        response_json = json.loads(chat_completion.choices[0].message.content)

        if response_json["is_full_article"] == True:
            return True

        return False

    async def gather_article_summaries(self, url: str, limit: int = 1) -> List[dict[str, str]]:
        article_links = await self.scraper.scrape_site(url)

        async with TaskGroup() as summary_task_group:
            results = []
            for link in article_links[:limit]:
                results.append(summary_task_group.create_task(
                    self.summarize_article(link)))

        return [r.result() for r in results]

    async def gather_article_embeddings(self, url: str, limit: int = 1) -> List[dict[str, str]]:
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

    async def retrieve_article_embeddings(self, url: str, limit: int = 1) -> List[dict[str, str]]:
        content = await self.scraper.scrape_content(url)
        chunks = self._chunk_text(content)

        async with TaskGroup() as summary_task_group:
            results = [
                summary_task_group.create_task(self.llm.get_embedding(chunk)) for chunk in chunks
            ]

        return [r.result() for r in results]

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
