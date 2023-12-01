
"""

List of steps we need to be able to take:

1. Navigate to the correct page of a site where we can find a list of articles
2. Extract the links to the articles

"""
from typing import List
import asyncio


class LLM:
    def __init__(self, temperature: int, model: str):
        self.temperature = temperature
        self.model = model
        # self.llm = ChatOpenAI(temperature=temperature, model=model)

    def summarize(self, content: str):
        pass

    def generate(self, prompt: str, content: str):
        self.llm.generate


class Scraper:

    def extract_article_links(self, extractor: "Extractor"):
        """
        After we go to the home page, LLM needs to examine the page and determine where to go next to find relevant content.

        At this point, there is an option to try to include some sort of user input to help LLM determine where to go next.
        It might be necessary in order to get the right content.

        As a first iteration, we can attempt to find what we expect is the correct content to scrape and error if we can't find it.
        """
        pass

    async def get_next_step(self, home_content: str) -> List[str]:
        """
        Take in html of home page and determine where to go next to find relevant content.
        """
        pass

    async def scrape_home_page(self):
        home_page = self.ascrape_playwright(self.url)
        next_pages = self.next_step(home_page)

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
    scraper = Scraper()
    result = asyncio.run(scraper.ascrape_playwright(
        "https://blog.colinbreck.com/choosing-a-webassembly-run-time/"))

    # get the full current path of this file
    import os

    current_file_path = os.path.abspath(__file__)
    current_directory = os.path.dirname(current_file_path)
    output_path = os.path.join(
        current_directory, "html_results/colinbreck_fullarticle.html")

    with open(output_path, "w") as f:
        f.write(result)
