# articles_igl_engine/core/search_indexes.py
from elasticsearch_dsl import Document, Text, Date


class ArticleIndex(Document):
    title = Text()
    content = Text()
    uploaded_at = Date()

    class Index:
        name = 'Articles'
