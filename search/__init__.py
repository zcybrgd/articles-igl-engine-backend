# myapp/__init__.py

from elasticsearch_dsl import connections
from elasticsearch import Elasticsearch

# connections.create_connection(alias='default', client=es)
connections.create_connection(
    alias="default",
    hosts=["https://localhost:9200"],
    verify_certs=False,
    basic_auth=("elastic", "yh38l6o*JY1wfuVXqZAP"),
)
