# search/management/commands/update_elasticsearch.py
import json
import hashlib
from django.core.management.base import BaseCommand
from elasticsearch.helpers import bulk
from elasticsearch import Elasticsearch
from ...search_indexes import ArticleIndex


class Command(BaseCommand):
    #Message d'aide :
    help = ('En cas de problème, veuillez mettre à jour votre index Elasticsearch avec la commande python '
            'manage.py update_elasticsearch')

    #Definition du port, host et de l'index utilisés
    def handle(self, *args, **options):
        es = Elasticsearch(['http://localhost:9200'])
        index = ArticleIndex._index._name

        #es.indices.delete(index=index) Décommenter cette instruction en cas de dupplications(permet de supprimer l'index existant)
        # Lecture des données par
        with open('search/articles.json') as json_file:
            articles_data = json.load(json_file)

        #Préparation des paramètres à indexer
        actions = [
            {
                '_op_type': 'index',
                '_index': index,
                #Définition d'un Id automatique
                '_id': hashlib.md5(f"{data['title']}_{data['authors']}_{data['date']}".encode('utf-8')).hexdigest(),
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
        # Indexation à l'aide de la fonction Bulk
        success, failed = bulk(es, actions)
        # Message de réussite de l'indexation
        self.stdout.write(self.style.SUCCESS(f'Successfully indexed {success} documents'))
        self.stdout.write(self.style.ERROR(f'Failed to index {failed} documents'))
