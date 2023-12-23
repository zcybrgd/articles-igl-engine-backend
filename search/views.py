# myapp/views.py
from django.shortcuts import render
from elasticsearch_dsl import Search
from elasticsearch_dsl.query import MultiMatch
from search.search_indexes import ArticleIndex


def search_articles(request):
    # query représente l'objet de la recherche effectuée par l'utilisateur
    query = request.GET.get('q', '')
    # Définition des paramètres sur lesquels effectuer la recherche
    fields = ['title', 'authors', 'keywords', 'text']
    # Recherche multimatch car elle concerne plusieurs paramètres
    multi_match_query = MultiMatch(query=query, fields=fields, type='phrase')
    # Etablissement de la recherche à l'aide de la fonction Search de Elasticsearch DSL
    s = Search(index='article_index').query(multi_match_query)
    # Récupération des résultats de recherche
    response = s.execute()
    # Choix des paramètres à afficher pour chaque résultat :
    results = [{'title': hit.title,
                'authors': hit.authors,
                'institutions': hit.institutions,
                'keywords': hit.keywords,
                'pdf_url': hit.pdf_url,
                'bibliographie': hit.bibliographie,
                'text': hit.text,
                'date': hit.date} for hit in response]

    return render(request, 'search_articles.html', {'query': query, 'results': results})
