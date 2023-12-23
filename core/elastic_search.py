from elasticsearch import Elasticsearch


es = Elasticsearch([{'host': 'localhost', 'port': 9200, 'scheme': 'http'}])

'''
def index_extracted_text(extracted_text):
    es.index(index='articles', doc_type='_doc', body={
        'text': extracted_text.text,
        'pdf_url': extracted_text.uploaded_pdf.pdf_file.url,
    })

def index_article_info(article_info, index_name='articles'):
    es = Elasticsearch()
    # Création de l'index s'il n'existe pas
    es.indices.create(index=index_name, ignore=400)
    # Indexation des données
    es.index(index=index_name, body=article_info)'''



