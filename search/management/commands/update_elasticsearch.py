# search/management/commands/update_elasticsearch.py
import json
from django.core.management.base import BaseCommand
from elasticsearch.helpers import bulk
from elasticsearch import Elasticsearch

# from ....search import search_indexes


class Command(BaseCommand):
    help = (
        "En cas de de problème, veuillez mettre à jour votre index Elasticsearch avec la commande python "
        "manage.py update_elasticsearch"
    )

    def handle(self, *args, **options):
        es = Elasticsearch(
            ["https://localhost:9200"],
            basic_auth=("elastic", "yh38l6o*JY1wfuVXqZAP"),
            verify_certs=False,
        )
        index = "scientific_articles"

        # Read data from JSON file
        with open("search/articles.json") as json_file:
            articles_data = json.load(json_file)

        actions = [
            {
                "_op_type": "index",
                "_index": index,
                # '_id': str(article.id), Elasticsearch will generate the IDs automatically
                "_source": {
                    "title": data.get("title", ""),
                    "authors": data.get("authors", ""),
                    "institutions": data.get("institutions", ""),
                    "keywords": data.get("keywords", ""),
                    "pdf_url": data.get("pdfUrl", ""),
                    "bibliographie": data.get("references", ""),
                    "text": data.get("content", ""),
                    "date": data.get("releaseDate", ""),
                    "summary": data.get("summary", ""),
                },
            }
            for data in articles_data
        ]

        es.delete_by_query(index=index, body={"query": {"match_all": {}}})
        success, failed = bulk(es, actions)

        self.stdout.write(
            self.style.SUCCESS(f"Successfully indexed {success} documents")
        )
        self.stdout.write(self.style.ERROR(f"Failed to index {failed} documents"))


# es = Elasticsearch(['http://localhost:9200'])
# indices = es.indices.get_alias("*")
# print (indices)
