from typing import List
import asyncio
from curator import Curator
from bs4 import BeautifulSoup
from urllib.parse import urlparse, urljoin, urldefrag
from os import path


class Scraper:
    """
    1. Scrape home route
    2. Ask curator if it is a full article
    3. if yes - asynchronously summarize and persist
    4. if no - use beautiful soup to gather all links
    5. go to each link and repeat
    """

    def __init__(self, curator: Curator) -> None:
        self.curator = curator

    # should consider using assistance of llm here; may be difficult to
    # exclude most edge cases otherwise for example "'https://blog.colinbreck.com/page/2/'"
    # Or -> we need to cache the urls we've already scraped in a set and avoid grabbing those
    def _should_include_url(self, original_url: str, url: str):
        if original_url == url:
            return False

        original_parse_result = urlparse(original_url)
        parse_result = urlparse(url)

        if (
            parse_result.hostname is None
            or "youtube" in parse_result.hostname
            or parse_result.hostname != original_parse_result.hostname
        ):
            return False

        return True

    async def extract_article_links(self, base_url: str, max_depth=1):

        links = []
        q = [(base_url, 0)]

        while len(q):
            link, depth = q.pop()

            page = await self.ascrape_playwright(url=link)
            soup = BeautifulSoup(page, "html.parser")

            for l in soup.find_all('a'):
                href = l.get("href")
                defragged = urldefrag(urljoin(base_url, href))
                full_url = defragged.url
                new_depth = depth + 1

                if self._should_include_url(base_url, full_url):
                    links.append(full_url)

                    if new_depth <= max_depth:
                        q.append((full_url, new_depth))

        return links

    async def scrape_article_content(self, url: str):
        home_page = await self.ascrape_playwright(url)
        is_full_article = await self.curator.is_full_article(home_page)

        if is_full_article:
            print("Full article found...")
            print(home_page)
            print()
        else:
            print("Looking for full articles elsewhere...")

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


if __name__ == "__main__":
    import os
    from llm import LLM

    llm = LLM()
    curator = Curator(llm=llm)
    scraper = Scraper(curator=curator)
    site_links = asyncio.run(scraper.extract_article_links(
        "https://blog.colinbreck.com"))
    print(site_links)

    # result = asyncio.run(scraper.scrape_site(
    #     "https://blog.colinbreck.com/an-interview-process-that-works-for-me/"))

    # current_file_path = os.path.abspath(__file__)
    # current_directory = os.path.dirname(current_file_path)
    # output_path = os.path.join(
    #     current_directory, "html_results/colinbreck_fullarticle.html")

    # with open(output_path, "w") as f:
    #     f.write(result
