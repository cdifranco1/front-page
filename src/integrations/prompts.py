

class ArticlePrompts:
    ARTICLE_CLASSIFIER_SYSTEM_PROMPT = """
    You are very familiar with blogs and websites.  You read html files and answer questions about them. You respond in json format only.
    """

    ARTICLE_CLASSIFIER_USER_PROMPT = """
        Given the html below, does this look like the location of a full, unified article? Or, does this look like an html file that may contain articles
        in the links within it.

        Respond with a json object using this schema: 
        {{"is_full_article": boolean}}

        HTML:
        {html}

        Response:
        """

    ARTICLE_SUMMARIZER_SYSTEM_PROMPT = """
    You provide an in-depth summaries of html documents you are provided for sophisticated readers on the topics covered.  You respond in json format only.
    """

    ARTICLE_SUMMARIZER_USER_PROMPT = """
        Respond with a json object using this schema: 
        {{"title": string, "summary": string}}

        HTML:
        {html}

        Response:
        """
