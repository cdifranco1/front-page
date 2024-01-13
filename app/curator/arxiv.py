
from langchain.document_loaders import OnlinePDFLoader
import requests
from bs4 import BeautifulSoup
from langchain.chat_models import ChatOpenAI
from langchain.text_splitter import RecursiveCharacterTextSplitter
from typing import List
from langchain.docstore.document import Document
from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate


"""
Arxiv:

https://arxiv.org/list/cs/new

Should generate article summaries 
"""


def fetch_arxiv_articles():
    url = "https://arxiv.org/list/cs/new"  # URL of the page you want to monitor
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')

    # extract all links in span with class list-identifier
    link_sections = soup.find_all('span', {'class': 'list-identifier'})

    # extract all divs with class meta
    article_details = soup.find_all('div', {'class': 'meta'})

    results = []

    # zip together
    for link_section, article in zip(link_sections, article_details):
        links = [l.get("href")
                 for l in link_section.find_all('a') if l.get("href").startswith("/pdf")]
        pdfLink = "https://arxiv.org" + links[0] if len(links) > 0 else None

        title = article.find(
            'div', {'class': 'list-title mathjax'}).text.strip()
        subjects = article.find('div', {'class': 'list-subjects'}).text.strip()
        authors = article.find('div', {'class': 'list-authors'}).text.strip()

        article = {
            'title': title,
            'subjects': subjects,
            'authors': authors,
            'pdfLink': pdfLink
        }

        results.append(article)

    return results


def load_pdf_from_arxiv(url) -> List[Document]:
    loader = OnlinePDFLoader(url)
    return loader.load()


def summarize_pdf(pdf_content: List[Document]):
    pass


def main():
    articles = fetch_arxiv_articles()
    one_article = articles[0]
    pdf_content: List[Document] = load_pdf_from_arxiv(one_article['pdfLink'])

    llm = ChatOpenAI(temperature=0, model="gpt-3.5-turbo-1106")

    # Grab the first 1000 tokens of the site
    splitter = RecursiveCharacterTextSplitter.from_tiktoken_encoder(
        separators=["\n\n", "\r\n", "\n"], chunk_size=10000, chunk_overlap=0)

    from langchain.chains.summarize import load_summarize_chain

    combine_template = """
    Write a concise summary of the following article in the style of the NY Times.

    Title: {title}
    Authors: {authors}
    Subjects: {subjects}

    Text: {text}

    CONCISE SUMMARY:
    """

    combine_prompt = PromptTemplate.from_template(combine_template, partial_variables={
                                                  "title": one_article['title'], "authors": one_article['authors'], "subjects": one_article['subjects']})

    map_template = """
    Write a short, high-level summary of the following. Do not refer to "the text" or "the article" in your summary. Just summarize the article
    as if you were the author.

    Text: {text}

    SHORT SUMMARY:
    """
    map_prompt = PromptTemplate.from_template(map_template)

    shortened = pdf_content[0].page_content

    texts = splitter.split_text(shortened)
    docs = splitter.create_documents(texts)

    chain = load_summarize_chain(
        llm, chain_type="map_reduce", combine_prompt=combine_prompt, map_prompt=map_prompt, verbose=False)
    return chain.run(docs)


if __name__ == '__main__':
    main()
    # print(load_result)
