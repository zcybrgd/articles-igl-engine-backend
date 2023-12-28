import hashlib
import json
from elasticsearch import Elasticsearch, TransportError
from search.search_indexes import ArticleIndex
class ModArticles:
    def __init__(self, json_file_path='core/pdf_unreviewed.json'):
        self.json_file_path = json_file_path
        self.articles = self.load_articles()

    def load_articles(self):
        with open(self.json_file_path) as json_file:
            return json.load(json_file)

    def save_articles(self):
        with open(self.json_file_path, 'w') as json_file:
            json.dump(self.articles, json_file, indent=2)

    def update_article(self, article_id, updated_data):
        for article in self.articles:
            if article.get('id') == article_id:
                article.update(updated_data)
                break
        self.save_articles()

    def delete_article(self, article_id):
        self.articles = [article for article in self.articles if article.get('id') != article_id]
        self.save_articles()

    def add_article(self, new_article_data):
        new_article_data['id'] = hashlib.md5(str(new_article_data).encode('utf-8')).hexdigest()
        self.articles.append(new_article_data)
        self.save_articles()

    def validate_article(self, article_id):
        self.articles = self.load_articles()
        article_to_validate = next((article for article in self.articles if article.get('id') == article_id), None)
        es_response = self.index_article(article_to_validate)
        if(es_response['success']):
            self.delete_article(article_id)
            return es_response
        else:
            return {'success': False, 'message': 'Unexpected error from server'}


    def index_article(self, article_data):
        es = Elasticsearch(['http://localhost:9200'],)
        index = ArticleIndex._index._name

        try:
            #the params to index
            action = {
                '_op_type': 'index',
                '_index': index,
                '_id': hashlib.md5(f"{article_data['title']}_{article_data['authors']}_{article_data['date']}".encode('utf-8')).hexdigest(),
                '_source': {
                    'title': article_data.get('title', ''),
                    'authors': article_data.get('authors', ''),
                    'institutions': article_data.get('institutions', ''),
                    'keywords': article_data.get('keywords', ''),
                    'pdf_url': article_data.get('pdf_url', ''),
                    'bibliographie': article_data.get('bibliographie', ''),
                    'abstract': article_data.get('abstract', ''),
                    'text': article_data.get('text', ''),
                    'date': article_data.get('date', ''),
                }
            }

            #index the new article
            es.index(index=index, body=action['_source'], id=action['_id'])
            return {'success': True, 'message': 'Article indexed successfully'}

        except TransportError as e:
            error_message = str(e)
            return {'success': False, 'message': f'Error indexing article: {error_message}'}

        except Exception as e:
            error_message = str(e)
            return {'success': False, 'message': f'Unexpected error: {error_message}'}