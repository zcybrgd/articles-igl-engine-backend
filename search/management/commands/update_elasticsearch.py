# search/management/commands/update_elasticsearch.py
import json
from django.core.management.base import BaseCommand
from elasticsearch.helpers import bulk
from elasticsearch import Elasticsearch
from ...search_indexes import ArticleIndex
from search.models import Article  # Replace with the correct import path to your Article model


class Command(BaseCommand):
    help = ('En cas de de problème, veuillez mettre à jour votre index Elasticsearch avec la commande python '
            'manage.py update_elasticsearch')

    def handle(self, *args, **options):
        es = Elasticsearch(['http://localhost:9200'])
        index = ArticleIndex._index._name

        # Read data from JSON file
        with open('search/articles.json') as json_file:
            articles_data = json.load(json_file)

        actions = [
            {
                '_op_type': 'index',
                '_index': index,
                # '_id': str(article.id), Elasticsearch will generate the IDs automatically
                '_source': {
                    'title': data.get('title', ''),
                    'authors': data.get('authors', ''),
                    'institutions': data.get('institutions', ''),
                    'keywords': data.get('keywords', ''),
                    'pdf_url': data.get('pdf_url', ''),
                    'bibliographie': data.get('bibliographie', ''),
                    'text': data.get('text', ''),
                    'date': data.get('date', ''),
                }
            }
            for data in articles_data
        ]

        success, failed = bulk(es, actions)

        self.stdout.write(self.style.SUCCESS(f'Successfully indexed {success} documents'))
        self.stdout.write(self.style.ERROR(f'Failed to index {failed} documents'))
