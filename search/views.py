from django.http import JsonResponse
from django.shortcuts import render
from elasticsearch_dsl import Search, Q
from elasticsearch_dsl.utils import AttrList
from elasticsearch_dsl.query import MultiMatch
from search.search_indexes import ArticleIndex


def search_articles(request):
    """_summary_

    Args:
        request (_type_): _description_

    Returns:
        _type_: _description_
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

    # Définition des paramètres sur lesquels effectuer la recherche
    fields = ["title", "authors", "keywords", "text"]

    if query:
        # Recherche multimatch car elle concerne plusieurs paramètres
        multi_match_query = MultiMatch(query=query, fields=fields, type="phrase")

        # Etablissement de la recherche à l'aide de la fonction Search de Elasticsearch DSL
        s = Search(index="article_index").query(multi_match_query)
    else:
        # Préparer la requete de recherche sur l'index
        s = Search(index="article_index")

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

    # Récupération des résultats de recherche
    response = s.execute()


    # Convert Elasticsearch results to a list of dictionaries
    results = [
        {
            "title": hit.title,
            "authors": list(hit.authors)
            if isinstance(hit.authors, AttrList)
            else hit.authors,
            "institutions": list(hit.institutions)
            if isinstance(hit.institutions, AttrList)
            else hit.institutions,
            "keywords": hit.keywords,
            "pdf_url": hit.pdf_url,
            "bibliographie": list(hit.bibliographie)
            if isinstance(hit.bibliographie, AttrList)
            else hit.bibliographie,
            "text": hit.text,
            "abstract": hit.abstract,
            "date": hit.date,
        }
        for hit in response
    ]

    # Return JSON response
    return JsonResponse({"query": query, "results": results})