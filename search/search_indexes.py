# myapp/search_indexes.py
from elasticsearch_dsl import Document, Text, Keyword, Date


class ArticleIndex(Document):
    title = Text()
    author = Keyword()
    institutions = Keyword()
    keywords = Keyword()
    pdf_url = Keyword()
    bibliographie = Keyword()
    text = Text()
    date = Date()

    class Index:
        name = 'article_index'
