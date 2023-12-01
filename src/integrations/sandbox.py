from os import path
from openai import OpenAI
import json
import pprint


def get_html_next_step() -> str:

    input = path.dirname(path.abspath(__file__)) + \
        "/html_results/colinbreck_fullarticle.html"

    content = ""
    with open(input, "r") as f:
        content = f.read()

    print("CONTENT")
    print(content)

    client = OpenAI()

    prompt = """
    Given the html below, does this look like the location of a full, unified article? Or, does this look like an html file that may contain articles
    in the links within it.

    Respond with a json object using this schema: 
    {{"is_full_article": boolean}}

    HTML:
    {html}

    Response:
    """

    system_prompt = "You are very familiar with blogs and websites.  You read html files and answer questions about them. You respond in json format only."

    chat_completion = client.chat.completions.create(
        temperature=0,
        response_format={
            "type": "json_object"
        },
        model="gpt-3.5-turbo-1106",
        messages=[
            {
                "role": "system",
                "content": system_prompt
            },
            {
                "role": "user",
                "content": prompt.format(html=content)
            }
        ]
    )

    print(chat_completion)

    response_json = chat_completion.choices[0].message.content
    print(response_json)

    _json = json.loads(response_json)
    pprint.pprint(_json)


if __name__ == "__main__":
    get_html_next_step()
