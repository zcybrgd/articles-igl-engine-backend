from elasticsearch import Elasticsearch
import time
from elasticsearch.exceptions import ConnectionError

# Establish a connection to your Elasticsearch instance
es = Elasticsearch(
    ["https://localhost:9200"],
    basic_auth=("elastic", "yh38l6o*JY1wfuVXqZAP"),
    verify_certs=False,
    # timeout="120s",
    # maxsize=10,
)

# Define the index settings and mappings
index_name = "scientific_articles"

index_settings = {
    "settings": {"number_of_shards": 1, "number_of_replicas": 1},
    "mappings": {
        "properties": {
            "title": {"type": "text"},
            "summary": {"type": "text"},
            "authors": {"type": "text"},
            "institutions": {"type": "text"},
            "keywords": {"type": "text"},
            "content": {"type": "text"},
            "releaseDate": {"type": "date"},
            "pdfUrl": {"type": "text"},
            "references": {"type": "text"},
        }
    },
}

with es as client:
    # Create the index with settings and mappings
    es.indices.create(index=index_name, body=index_settings)
