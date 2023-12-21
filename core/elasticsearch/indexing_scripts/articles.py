from click import BaseCommand
from elasticsearch_dsl import Document, Text, Date
from elasticsearch_dsl.connections import connections
import json

# Define your Elasticsearch connection
connections.create_connection(hosts=['http://localhost:9200'])

# Define your Document class
class ScientificArticle(Document):
    title = Text()
    summary = Text()
    authors = Text()
    institutions = Text()
    keywords = Text()
    content = Text()
    releaseDate = Date()
    pdfUrl = Text()
    references = Text()

    class Index:
        name = 'scientific_articles'

from elasticsearch_dsl import Document, Text, Date, connections
import json

# Define your Elasticsearch connection
connections.create_connection(hosts=['http://localhost:9200'])

# Define your Document class
class ScientificArticle(Document):
    title = Text()
    summary = Text()
    authors = Text()
    institutions = Text()
    keywords = Text()
    content = Text()
    releaseDate = Date()
    pdfUrl = Text()
    references = Text()

    class Index:
        pass 

# Indexation
def index_articles(json_file_path, index_name):
    # Assign the provided index name to the Index class
    ScientificArticle.Index.name = index_name

    # Read the JSON file and load its content
    with open(json_file_path, 'r') as file:
        articles_data = json.load(file)

    # Index each article into Elasticsearch
    for article_data in articles_data:
        article = ScientificArticle(
            title=article_data.get('title', ''),
            authors=article_data.get('authors', ''),
            summary=article_data.get('summary', ''),
            institutions=article_data.get('institutions', ''),
            keywords=article_data.get('keywords', ''),
            content=article_data.get('content', ''),
            releaseDate=article_data.get('releaseDate', ''),
            pdfUrl=article_data.get('pdfUrl', ''),
            references=article_data.get('references', '')
        )
        article.save()


#index_articles(json_file_path, desired_index_name)
