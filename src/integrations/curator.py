from os import path
import json
from prompts import ArticlePrompts
from llm import LLM, ChatCompletionMessage


class Curator:
    def __init__(self, llm: LLM) -> None:
        self.llm = llm

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


if __name__ == "__main__":
    input = path.dirname(path.abspath(__file__)) + \
        "/html_results/colinbreck.html"

    content = ""
    with open(input, "r") as f:
        content = f.read()

    llm = LLM()
    curator = Curator(llm)

    print(curator.is_full_article(content))
