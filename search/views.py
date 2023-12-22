# myapp/views.py
from django.shortcuts import render
from elasticsearch_dsl import Search
from elasticsearch_dsl.query import MultiMatch
from search.search_indexes import ArticleIndex


def search_articles(request):
    query = request.GET.get('q', '')
    fields = ['title', 'authors', 'keywords']
    multi_match_query = MultiMatch(query=query, fields=fields, type='phrase')
    s = Search(index='article_index').query(multi_match_query)
    response = s.execute()
    results = [{'title': hit.title,
                'authors': hit.authors,
                'institutions': hit.institutions,
                'keywords': hit.keywords,
                'pdf_url': hit.pdf_url,
                'bibliographie': hit.bibliographie,
                'text': hit.text,
                'date': hit.date} for hit in response]
    return render(request, 'search_articles.html', {'query': query, 'results': results})
