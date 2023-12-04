
from openai import OpenAI
from typing import List


class ChatCompletionMessage:
    def __init__(self, role: str, content: str) -> None:
        self.role = role
        self.content = content


class LLM:
    def __init__(self, client: OpenAI = OpenAI()) -> None:
        self.client = client

    def get_response(self, messages: List[ChatCompletionMessage]) -> str:
        return self.client.chat.completions.create(
            temperature=0,
            response_format={
                "type": "json_object"
            },
            model="gpt-3.5-turbo-1106",
            messages=[m.__dict__ for m in messages]
        )
