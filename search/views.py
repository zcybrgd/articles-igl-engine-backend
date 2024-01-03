from django.http import JsonResponse
from elasticsearch import client
from elasticsearch_dsl import Search
from elasticsearch_dsl.query import MultiMatch
from elasticsearch_dsl.utils import AttrList
from rest_framework.decorators import api_view


def search_articles(request):
    query = request.GET.get('q', '')
    fields = ['title', 'authors', 'keywords', 'text', 'abstract']
    multi_match_query = MultiMatch(query=query, fields=fields, type='phrase')
    s = Search(index='article_index').query(multi_match_query).filter('term', status='validated')
    response = s.execute()
    # Convert Elasticsearch results to a list of dictionaries
    results = [{
                'id': hit.meta.id,
                'title': hit.title,
                'authors': list(hit.authors) if isinstance(hit.authors, AttrList) else hit.authors,
                'institutions': list(hit.institutions) if isinstance(hit.institutions, AttrList) else hit.institutions,
                'keywords': hit.keywords,
                'pdf_url': hit.pdf_url,
                'bibliographie': list(hit.bibliographie) if isinstance(hit.bibliographie,
                                                                       AttrList) else hit.bibliographie,
                'abstract': hit.abstract,
                'text': hit.text,
                'date': hit.date} for hit in response]

    # Return JSON response
    return JsonResponse({'query': query, 'results': results})


@api_view(['GET'])
def total_articles(request):
    search = Search(index='article_index')
    # Count search results
    total = search.count()
    # Return JSON response
    return JsonResponse({'total': total})


@api_view(['GET'])
def unreviewed_articles(request):
    search = Search(index='article_index').filter('term', status='unreviewed')
    # Count search results
    total = search.count()
    # Return JSON response
    return JsonResponse({'total': total})
