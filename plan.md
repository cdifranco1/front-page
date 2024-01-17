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

# Changelog

- initial work

  - [x] scrape content from single article and create embeddings
  - [x] persist embeddings in postgres using pgvecto.rs
  - [x] ability to search embeddings and return canonical document urls

- enhanced scraping capabilities:

  - [-] index entire site and use llm with rate limiting
  - [ ] ability to transcribe and index podcasts

- enhanced search capabilities

  - [ ] ability to perform more advanced search and/or transform outputs (i.e. summarization) using llm
  - [ ] ability to display html documents in app
  - [ ] ability to ask questions about the canonical documents being returned

- CLI?
- Web app?
- Mobile app?
