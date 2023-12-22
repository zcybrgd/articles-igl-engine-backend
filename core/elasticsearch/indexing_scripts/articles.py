import sys
import datetime
import json
import os
import logging
from elasticsearch import Elasticsearch
from elasticsearch.helpers import streaming_bulk

# ES Configuration start
es_hosts = [
    "http://localhost:9200",
]
es_api_user = "user"
es_api_password = "pw"
index_name = "scientific_articles"
chunk_size = 500
errors_before_interrupt = 1
refresh_index_after_insert = False
max_insert_retries = 3
yield_ok = False  # if set to False will skip successful documents in the output
# ES Configuration end

filename = "D:/1CS/IGL/TP/articles-igl-engine-backend/core/elasticsearch/indexing_scripts/articles.json"

logging.info("Importing data from {}".format(filename))

es = Elasticsearch(
    es_hosts,
    # http_auth=(es_api_user, es_api_password),
    sniff_on_start=True,  # sniff before doing anything
    sniff_on_connection_fail=True,  # refresh nodes after a node fails to respond
    sniffer_timeout=60,  # and also every 60 seconds
    retry_on_timeout=True,  # should a timeout trigger a retry on a different node?
)


def data_generator():
    f = open(filename)
    data = json.load(f)
    for d in data:
        yield {**json.loads(json.dumps(d)), **{"_index": index_name}}
        # print("line:",d)


# data_generator()

errors_count = 0

for ok, result in streaming_bulk(
    es,
    data_generator(),
    chunk_size=chunk_size,
    refresh=refresh_index_after_insert,
    max_retries=max_insert_retries,
    yield_ok=yield_ok,
):
    if ok is not True:
        logging.error("Failed to import data")
        logging.error(str(result))
        errors_count += 1

        if errors_count == errors_before_interrupt:
            logging.fatal("Too many import errors, exiting with error code")
            exit(1)

print("Documents loaded to Elasticsearch")


###########################################################################################

"""from click import BaseCommand
from elasticsearch_dsl import Document, Text, Date
from elasticsearch_dsl.connections import connections
import json

# Define your Elasticsearch connection
connections.create_connection(hosts=["http://localhost:9200"])

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
        name = 'p'


# Indexation
def index_articles(json_file_path, index_name):
    # Assign the provided index name to the Index class
    ScientificArticle.Index.name = index_name

    # Read the JSON file and load its content
    with open(json_file_path, "r") as file:
        articles_data = json.load(file)

    # Index each article into Elasticsearch
    for article_data in articles_data:
        article = ScientificArticle(
            title=article_data.get("title", ""),
            authors=article_data.get("authors", ""),
            summary=article_data.get("summary", ""),
            institutions=article_data.get("institutions", ""),
            keywords=article_data.get("keywords", ""),
            content=article_data.get("content", ""),
            releaseDate=article_data.get("releaseDate", ""),
            pdfUrl=article_data.get("pdfUrl", ""),
            references=article_data.get("references", ""),
        )
        article.save()

json_file_path = 'D:/1CS/IGL/TP/articles-igl-engine-backend/core/elasticsearch/indexing_scripts/articles.json'
desired_index_name = 'scientific_articles'
index_articles(json_file_path, desired_index_name) """
