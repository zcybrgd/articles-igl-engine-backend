from django.http import JsonResponse
from elasticsearch_dsl.utils import AttrList
from elasticsearch_dsl import Search, Q
from elasticsearch_dsl.query import MultiMatch
from rest_framework.decorators import api_view, permission_classes
from rest_framework import permissions

def search_articles(request):
    """
        Perform a search query on articles using various filters.

        Args:
            request (HttpRequest): The HTTP request object.

        Returns:
            JsonResponse: JSON response containing the search query and results.
    """
    # query représente l'objet de la recherche effectuée par l'utilisateur
    query = request.GET.get("q", "")

    # query_mots_cles représente la valeur de la requete du filtre par mots clés
    query_mots_cles = request.GET.get("mots_cles", "")

    # query_auteurs représente la valeur de la requete du filtre par auteurs
    query_auteurs = request.GET.get("auteurs", "")

    # query_instit représente la valeur de la requete du filtre par institutions
    query_instit = request.GET.get("institutions", "")

    # start_date représente la valeur de la requete du filtre par date (récuperer la date début)
    start_date = request.GET.get("start_date")

    # end_date représente la valeur de la requete du filtre par date (récuperer la date fin)
    end_date = request.GET.get("end_date")

    fields = ['title', 'authors', 'keywords', 'text', 'abstract']
    if query:
        # Recherche multimatch car elle concerne plusieurs paramètres
        multi_match_query = MultiMatch(query=query, fields=fields, type="phrase")
        # Etablissement de la recherche à l'aide de la fonction Search de Elasticsearch DSL
        s = Search(index="article_index").query(multi_match_query).filter('term', status='validated')
    else:
        # Préparer la requete de recherche sur l'index
        s = Search(index="article_index").filter('term', status='validated')


     # Effectuer le filtre par mots clés sur les résultats obtenu dans la recerche générale
    if query_mots_cles:
        s = s.query(Q("match", keywords=query_mots_cles))

    # Effectuer le filtre par auteurs sur les résultats obtenu dans la recerche générale
    if query_auteurs:
        s = s.query(Q("match", authors=query_auteurs))

    # Effectuer le filtre par institutions sur les résultats obtenu dans la recerche générale
    if query_instit:
        s = s.query(Q("match", institutions=query_instit))

    # Effectuer le filtre par période sur les résultats obtenu dans la recerche générale
    if start_date and end_date:
        s = s.filter("range", date={"gte": start_date, "lte": end_date})

    response = s.execute()

    # Convert Elasticsearch results to a list of dictionaries
    results = [{'id': hit.meta.id,
                'title': hit.title,
                'authors': list(hit.authors) if isinstance(hit.authors, AttrList) else hit.authors,
                'institutions': list(hit.institutions) if isinstance(hit.institutions, AttrList) else hit.institutions,
                'keywords': hit.keywords,
                'pdf_url': hit.pdf_url,
                'bibliographie': list(hit.bibliographie) if isinstance(hit.bibliographie, AttrList) else hit.bibliographie,
                'abstract': hit.abstract,
                'text': hit.text,
                'date': hit.date} for hit in response]

    return JsonResponse({'query': query, 'results': results})




@api_view(['GET'])
@permission_classes((permissions.AllowAny,))
def total_articles(request):
    """
        Get the total count of articles.

        Args:
            request (HttpRequest): The HTTP request object.

        Returns:
            JsonResponse: JSON response containing the total count of articles.
    """
    search = Search(index='article_index')
    total = search.count()
    return JsonResponse({'total': total})


@api_view(['GET'])
@permission_classes((permissions.AllowAny,))
def unreviewed_articles(request):
    """
        Get the count of unreviewed articles, that should be reviewed by Moderators

        Args:
            request (HttpRequest): The HTTP request object.

        Returns:
            JsonResponse: JSON response containing the count of unreviewed articles.
    """
    search = Search(index='article_index').filter('term', status='unreviewed')
    # Count search results
    total = search.count()
    return JsonResponse({'total': total})
