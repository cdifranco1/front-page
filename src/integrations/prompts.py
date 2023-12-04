

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
