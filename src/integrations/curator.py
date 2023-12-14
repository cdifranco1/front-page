from os import path
import json
from prompts import ArticlePrompts
from llm import LLM, ChatCompletionMessage
from scraper import Scraper
from typing import List


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

    async def gather_articles(self, url: str, limit: int = 5) -> List[dict[str, str]]:
        article_links = self.scraper.scrape_site(url)

        # create a thread pool, and for each link, check if it's a full article
        # if it is a full article,
        #    store in the db, and pass the content with a prompt to the llm
        #       store llm output in the db

    async def summarize(link: str, content: str) -> str:
        pass


if __name__ == "__main__":
    input = path.dirname(path.abspath(__file__)) + \
        "/html_results/colinbreck.html"

    content = ""
    with open(input, "r") as f:
        content = f.read()

    llm = LLM()
    curator = Curator(llm)

    print(curator.is_full_article(content))
