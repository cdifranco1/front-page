from typing import List
from typing import Optional
from bs4 import BeautifulSoup
from urllib.parse import urlparse, urljoin, urldefrag
import requests
import feedparser
from src.integrations.llm import LLM, ChatCompletionMessage
from src.integrations.prompts import ArticlePrompts
import re
import json


class Scraper:
    """
    1. Scrape home route
    2. Ask curator if it is a full article
    3. if yes - asynchronously summarize and persist
    4. if no - use beautiful soup to gather all links
    5. go to each link and repeat
    """

    def __init__(self, llm: LLM) -> None:
        self.llm = llm

    def find_rss_feed(self, url: str) -> str:
        try:
            response = requests.get(url)
            soup = BeautifulSoup(response.content, 'html.parser')

            for link in soup.find_all('link', type='application/rss+xml'):
                rss_url = link.get('href')
                print(f"Found RSS feed: {rss_url}")
                # Optionally verify the RSS URL here

                return rss_url

        except requests.RequestException as e:
            print(f"Error: {e}")

    def get_rss_feed(self, base_url: str) -> List[str]:
        rss_url = self.find_rss_feed(base_url)
        feed = feedparser.parse(rss_url)

        return feed

    async def find_sitemap_path_from_robots_txt(self, base_url: str) -> Optional[str]:
        robots_text_url = urljoin(base_url, "/robots.txt")
        response = requests.get(robots_text_url)

        print(response)
        if response.status_code == 200:
            lines = response.text.split("\n")

            for line in lines:
                if line.startswith("Sitemap:"):
                    return line.split(": ")[1]

        return None

    async def get_sitemap_url(self, base_url: str) -> Optional[str]:
        optimistic_site_map_url = urljoin(base_url, "/sitemap.xml")
        print(f"Optimistic sitemap URL: {optimistic_site_map_url}")

        response = requests.get(optimistic_site_map_url)
        print(response)
        if response.status_code == 200:
            return optimistic_site_map_url
        elif response.status_code == 404:
            sitemap_path = await self.find_sitemap_path_from_robots_txt(base_url)
            return urljoin(base_url, sitemap_path)

        return None

    def _should_include_url(self, url: str, original_url: str, seen: set):
        if original_url == url:
            return False

        original_parse_result = urlparse(original_url)
        parse_result = urlparse(url)

        if (
            (parse_result.hostname is None
             or "youtube" in parse_result.hostname
             or parse_result.hostname != original_parse_result.hostname
             or "images" in parse_result.path
             or "/tag" in parse_result.path
             or "/tags" in parse_result.path
             or "/talks" in parse_result.path
             )
            or url in seen
        ):
            return False

        # if with_llm_assistance:
        #     page_response = requests.get(url)
        #     print(page_response)
        #     print(page_response.headers["content-type"])
        #     if page_response.status_code != 200 or "text/html" not in page_response.headers["content-type"]:
        #         return False
        #     is_full_article = await self.is_full_article(page_response.text)
        #     return is_full_article
        # else:
        return True

    async def is_full_article(self, html_content: str) -> bool:
        max_tokens = 16385
        max_text_length_estimate = max_tokens * 3

        system_message = ChatCompletionMessage(
            role="system",
            content=ArticlePrompts.ARTICLE_CLASSIFIER_SYSTEM_PROMPT
        )
        user_message = ChatCompletionMessage(
            role="user",
            content=ArticlePrompts.ARTICLE_CLASSIFIER_USER_PROMPT.format(
                html=html_content[:max_text_length_estimate])
        )
        chat_completion = await self.llm.get_response([system_message, user_message], response_format={
            "type": "json_object"
        }, model='gpt-3.5-turbo-1106')

        response_json = json.loads(chat_completion.choices[0].message.content)

        if response_json["is_full_article"] == True:
            return True

        return False

    # We can improve this search to only look for the links most likely to bring us
    # to a full article
    async def extract_all_article_links(self, base_url: str, max_depth=1) -> List[str]:
        seen = set()

        q = [(base_url, 0)]

        while len(q):
            link, depth = q.pop()

            page = await self.ascrape_playwright(url=link)
            soup = BeautifulSoup(page, "html.parser")

            for l in soup.find_all(href=True):
                href = l.get("href")
                defragged = urldefrag(urljoin(base_url, href))
                full_url = defragged.url
                new_depth = depth + 1

                if self._should_include_url(base_url, full_url, seen):
                    seen.add(full_url)

                    if new_depth <= max_depth:
                        q.append((full_url, new_depth))

        return list(seen)

    async def ascrape_playwright(self, url) -> str:
        """
        Asynchronously scrape the content of a given URL using Playwright's async API.

        Args:
            url (str): The URL to scrape.

        Returns:
            str: The scraped HTML content or an error message if an exception occurs.

        """
        from playwright.async_api import async_playwright

        results = ""
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            try:
                page = await browser.new_page()
                await page.goto(url)
                results = await page.content()  # Simply get the HTML content
            except Exception as e:
                results = f"Error: {e}"
            await browser.close()
        return results

    # TODO: improve the text extraction to remove newlines
    async def scrape_content(self, url: str) -> str:
        html = await self.ascrape_playwright(url)
        soup = BeautifulSoup(html, "html.parser")
        text = soup.get_text()
        cleaned = re.sub(r'\s+', ' ', text)

        return cleaned

    # probably need better error handling
    async def _fetch_sitemap(self, sitemap_url: str) -> str:
        response = requests.get(sitemap_url)

        if response.status_code == 200:
            return response.content
        else:
            return None

    # for optimization, we need to store the actual content, not just return the links
    # for now just extract the links
    async def extract_sitemap_post_links(self, sitemap_url: str, base_url: str) -> Optional[list[str]]:
        print(sitemap_url)

        async def get_urls_from_sitemap_response(content: str) -> List[str]:
            soup = BeautifulSoup(content, features="xml")
            return [loc.text for loc in soup.find_all("loc") if self._should_include_url(loc.text, base_url, set())]

        sitemap_response = await self._fetch_sitemap(sitemap_url)
        if sitemap_response is None:
            return None

        sitemaps = BeautifulSoup(
            sitemap_response, features="xml").find_all("sitemap")

        if len(sitemaps) == 0:
            return await get_urls_from_sitemap_response(sitemap_response)

        results = []
        for sitemap in sitemaps:
            location = sitemap.find("loc").text
            response = await self._fetch_sitemap(location)
            urls = await get_urls_from_sitemap_response(response)
            results.extend(urls)

        return results

    # Can also try to use way back machine to improve performance and rate of success
    async def scrape_site(self, url: str) -> List[str]:
        """
        Scrape a given URL for all potential article links.
        """
        sitemap_url = await self.get_sitemap_url(url)
        print(f"Sitemap URL: {sitemap_url}")
        if sitemap_url is not None:
            post_links = await self.extract_sitemap_post_links(sitemap_url, url)
            if post_links is None:
                return await self.extract_all_article_links(url)
            return post_links
        elif sitemap_url is None:
            return await self.extract_all_article_links(url)
