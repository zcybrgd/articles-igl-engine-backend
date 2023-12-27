from django.http import JsonResponse
from elasticsearch_dsl import Search
from elasticsearch_dsl.query import MultiMatch
from elasticsearch_dsl.utils import AttrList
from search.search_indexes import ArticleIndex

def search_articles(request):
    query = request.GET.get('q', '')
    fields = ['title', 'authors', 'keywords', 'text','abstract']
    multi_match_query = MultiMatch(query=query, fields=fields, type='phrase')
    s = Search(index='article_index').query(multi_match_query)
    response = s.execute()

    # Convert Elasticsearch results to a list of dictionaries
    results = [{'title': hit.title,
                'authors': list(hit.authors) if isinstance(hit.authors, AttrList) else hit.authors,
                'institutions': list(hit.institutions) if isinstance(hit.institutions, AttrList) else hit.institutions,
                'keywords': hit.keywords,
                'pdf_url': hit.pdf_url,
                'bibliographie': list(hit.bibliographie) if isinstance(hit.bibliographie, AttrList) else hit.bibliographie,
                'abstract':hit.abstract,
                'text': hit.text,
                'date': hit.date} for hit in response]

    # Return JSON response
    return JsonResponse({'query': query, 'results': results})
