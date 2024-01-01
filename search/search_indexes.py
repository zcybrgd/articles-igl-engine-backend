# myapp/search_indexes.py
from elasticsearch_dsl import Document, Text, Keyword, Date


    #Création d'un document ElasticSearch DSL pour notre Article
class ArticleIndex(Document):
    #Definition des types des paramètres à indexer
    title = Text()
    author = Keyword()
    institutions = Keyword()
    keywords = Keyword()
    pdf_url = Keyword()
    bibliographie = Keyword()
    abstract = Text()
    text = Text()
    date = Date()
    status = Text()


    class Index:
        #Ceci représente le nom de  l'index à construire
        name = 'article_index'
