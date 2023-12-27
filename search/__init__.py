# myapp/__init__.py

from elasticsearch_dsl import connections

connections.create_connection(alias='default', hosts=['http://localhost:9200'])
