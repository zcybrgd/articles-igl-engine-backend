import hashlib
from elasticsearch import Elasticsearch, TransportError, exceptions as es_exceptions
from search.search_indexes import ArticleIndex
class ModArticles:
    """
        Class for managing articles in Elasticsearch, these are the main function of the Moderator's requests

        This class provides methods for indexing, deleting, updating, and retrieving articles in Elasticsearch.

        Attributes:
            es (Elasticsearch): Elasticsearch client instance.
    """
    def __init__(self):
        """
               Initialize ModArticles object.

               Initializes the Elasticsearch client.
        """
        self.es = Elasticsearch(['http://localhost:9200', 'http://elasticsearch:9200'],)
    def index_article(self, article_data):
        """
               Index an article in Elasticsearch.

               Args:
                   article_data (dict): Dictionary containing article data.

               Returns:
                   dict: Dictionary indicating success or failure of the operation.
        """
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
                    'status':'unreviewed'
                }
            }

            #index the new article
            self.es.index(index=index, body=action['_source'], id=action['_id'])
            return {'success': True, 'message': 'Article indexed successfully'}

        except TransportError as e:
            error_message = str(e)
            return {'success': False, 'message': f'Error indexing article: {error_message}'}

        except Exception as e:
            error_message = str(e)
            return {'success': False, 'message': f'Unexpected error: {error_message}'}

    def delete_from_elastic_search(self, article_id):
        """
                Delete an article from Elasticsearch.

                Args:
                    article_id (str): ID of the article to delete.

                Returns:
                    dict: Dictionary indicating success or failure of the operation.
        """
        index = ArticleIndex._index._name
        try:
            self.es.delete(index=index, id=article_id)
            return {'success': True, 'message': 'Article deleted successfully from Elasticsearch'}
        except es_exceptions.NotFoundError:
            return {'success': False, 'message': 'Article not found in Elasticsearch'}
        except es_exceptions.TransportError as e:
            error_message = str(e)
            return {'success': False, 'message': f'Error deleting article from Elasticsearch: {error_message}'}
        except Exception as e:
            error_message = str(e)
            return {'success': False, 'message': f'Unexpected error: {error_message}'}

    def update_to_elastic_search(self, article_id):
        """
                Update the status of an article in Elasticsearch to 'validated'.

                Args:
                    article_id (str): ID of the article to update.

                Returns:
                    dict: Dictionary indicating success or failure of the operation.
        """
        index = ArticleIndex._index._name
        try:
            es_article = self.es.get(index=index, id=article_id)
            updated_article = {**es_article['_source'], 'status': 'validated'}
            self.es.index(index=index, id=article_id, body=updated_article)
            return {'success': True, 'message': 'Article updated successfully in Elasticsearch'}
        except es_exceptions.NotFoundError:
            return {'success': False, 'message': 'Article not found in Elasticsearch'}
        except es_exceptions.TransportError as e:
            error_message = str(e)
            return {'success': False, 'message': f'Error updating article in Elasticsearch: {error_message}'}
        except Exception as e:
            error_message = str(e)
            return {'success': False, 'message': f'Unexpected error: {error_message}'}

    def get_unreviewed_documents(self):
        """
                Retrieve unreviewed documents from Elasticsearch.

                Returns:
                    list: List of unreviewed documents.
        """
        index = ArticleIndex._index._name
        query = {
            "query": {
                "bool": {
                    "must": [
                        {"match": {"status": "unreviewed"}}
                    ]
                }
            }
        }
        response = self.es.search(index=index, body=query)
        documents = []
        for hit in response['hits']['hits']:
            doc = hit['_source']
            doc['id'] = hit['_id']
            documents.append(doc)
        return documents

    def modify_elastic_search(self,aid,data):
        """
                Modify an article in Elasticsearch.

                Args:
                    article_id (str): ID of the article to modify.
                    data (dict): Updated data for the article.

                Returns:
                    dict: Dictionary indicating success or failure of the operation.
        """
        index = ArticleIndex._index._name
        response = self.es.update(index=index, id=aid, body={"doc": data})
        if response['result'] == 'updated':
            return {'success': True, 'message': 'Article updated successfully in Elasticsearch'}
        else:
            return {'success': False, 'message': 'Error updating article in Elasticsearch'}