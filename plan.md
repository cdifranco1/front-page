# Steps for Extracting All Relevant Articles from a Site

1. Go to the site using a headless browser
2. From rendered html, scrape ['a', 'p', 'h*', 'li']

   - scrape recursively for a max number of times (like 5 iterations) and gather into a tree

   ```
        {
            "url": "https://blog.colinbreck.com/"
            "
        }
   ```

3. ## Feed content to LLM:
