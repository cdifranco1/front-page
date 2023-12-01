

from typing import List
from langchain.docstore.document import Document
from playwright.async_api import async_playwright
from langchain.chat_models import ChatOpenAI
from langchain.chains import create_extraction_chain

import pprint

from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.document_loaders import AsyncChromiumLoader
from langchain.document_transformers import BeautifulSoupTransformer


def test_one():
    # load html
    loader = AsyncChromiumLoader(["https://www.wsj.com"])
    html = loader.load()

    # Transform
    bs_transformer = BeautifulSoupTransformer()
    docs_transformed = bs_transformer.transform_documents(
        html, tags_to_extract=["span"]
    )

    # Result
    docs_transformed[0].page_content[0:500]


llm = ChatOpenAI(temperature=0, model="gpt-3.5-turbo-0613")


def extract_arxiv():
    loader = AsyncChromiumLoader(["https://arxiv.org/list/cs/new"])
    html: List[Document] = loader.load()

    # Transform
    bs_transformer = BeautifulSoupTransformer()
    docs_transformed = bs_transformer.transform_documents(
        html, tags_to_extract=["a"]
    )
    for doc in docs_transformed[:3]:
        print(doc.page_content)
    print(docs_transformed)


schema = {
    "properties": {
        "news_article_title": {"type": "string"},
        "news_article_summary": {"type": "string"},
    },
    "required": ["news_article_title", "news_article_summary"],
}


def extract(content: str, schema: dict):
    return create_extraction_chain(schema=schema, llm=llm).run(content)


async def run():
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page()
        await page.goto('https://www.wsj.com')
        content = await page.content()
        print(content)
        await browser.close()


def scrape_with_playwright(urls, schema):
    loader = AsyncChromiumLoader(urls)
    docs = loader.load()

    bs_transformer = BeautifulSoupTransformer()
    docs_transformed = bs_transformer.transform_documents(
        docs, tags_to_extract=["span"]
    )

    for d in docs_transformed:
        print("Page content")
        print(d.page_content)
        print()

    print("Extracting content with LLM")

    # Grab the first 1000 tokens of the site
    splitter = RecursiveCharacterTextSplitter.from_tiktoken_encoder(
        chunk_size=1000, chunk_overlap=0
    )
    splits = splitter.split_documents(docs_transformed)

    # Process the first split
    extracted_content = extract(schema=schema, content=splits[0].page_content)
    pprint.pprint(extracted_content)
    # return extracted_content


def scrape_wsj():
    urls = ["https://www.wsj.com"]
    scrape_with_playwright(urls, schema=schema)
    # print(extracted_content)


if __name__ == "__main__":
    extract_arxiv()
