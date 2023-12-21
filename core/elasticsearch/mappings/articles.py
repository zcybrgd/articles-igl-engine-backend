from elasticsearch import Elasticsearch

# Initialize Elasticsearch client
# es = Elasticsearch([{'host': 'localhost', 'port': 9200}])
es = Elasticsearch("http://localhost:9200")

# Index name
index_name = "scientific_articles"

# Mapping definition
mapping = {
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
    }
}


# es.indices.create(index=index_name, body=mapping)
indices = es.indices.get_alias().keys()
print(indices)
