# myapp/views.py
from django.shortcuts import render
from elasticsearch_dsl import Search, Q
from elasticsearch_dsl.query import MultiMatch


def search_articles(request):
    query = request.GET.get("query", "")
    query_mots_cles = request.GET.get("mots_cles", "")
    query_auteurs = request.GET.get("auteurs", "")
    query_instit = request.GET.get("institutions", "")
    start_date = request.GET.get("start_date")
    end_date = request.GET.get("end_date")
    # query = request.GET.get("q", "")

    s = Search(index="scientific_articles")

    # Constructing a more complex query based on different parameters
    if query:
        s = s.query(
            Q(
                "multi_match",
                query=query,
                fields=["title", "authors", "keywords"],
                type="phrase",
            )
        )
    if query_mots_cles:
        s = s.query(Q("match", keywords=query_mots_cles))
    if query_auteurs:
        s = s.query(Q("match", authors=query_auteurs))
    if query_instit:
        s = s.query(Q("match", institutions=query_instit))
    if start_date and end_date:
        s = s.filter("range", date={"gte": start_date, "lte": end_date})

    response = s.execute()

    """fields = ["title", "authors", "keywords"]
    multi_match_query = MultiMatch(query=query, fields=fields, type="phrase")
    s = Search(index="scientific_articles").query(multi_match_query)
    response = s.execute()"""

    results = []
    for hit in response:
        results.append(
            {
                "title": hit.title,
                "authors": hit.authors,
                "institutions": hit.institutions,
                "keywords": hit.keywords,
                "pdf_url": hit.pdf_url,
                "bibliographie": hit.bibliographie,
                "text": hit.text,
                "date": hit.date,
                "summary": hit.summary,
            }
        )

    return render(
        request,
        "search_articles.html",
        {"query": query, "results": results},
    )


'''def search_articles(request):
    query = request.GET.get("q", "")
    selected_author = request.GET.get("author", "")

    fields = ["title", "authors", "keywords"]
    multi_match_query = MultiMatch(query=query, fields=fields, type="phrase")
    s = Search(index="scientific_articles").query(multi_match_query)
    response = s.execute()

    # Extract unique authors from search results
    authors = list(set([author for hit in response for author in hit.authors]))

    # Filter the response if an author is selected
    """if selected_author:
        s = s.filter("term", authors=selected_author)"""
    # Re-execute the query with author filter

    # Extract unique results based on title
    unique_results = []
    unique_titles = set()

    for hit in response:
        if hit.title not in unique_titles:
            unique_titles.add(hit.title)
            unique_results.append(
                {
                    "title": hit.title,
                    "authors": hit.authors,
                    "institutions": hit.institutions,
                    "keywords": hit.keywords,
                    "pdf_url": hit.pdf_url,
                    "bibliographie": hit.bibliographie,
                    "text": hit.text,
                    "date": hit.date,
                    "summary": hit.summary,
                }
            )

    if selected_author:
        unique_results = [
            result
            for result in unique_results
            if any(author in selected_author for author in result["authors"])
        ]

    for r in unique_results:
        print("resultat:", r)
        print("\n")
    return render(
        request,
        "search_articles.html",
        {"query": query, "results": unique_results, "authors": authors},
    )
'''
"""def search_articles(request):
    
    query = request.GET.get("q", "")
    fields = ["title", "authors", "keywords"]
    multi_match_query = MultiMatch(query=query, fields=fields, type="phrase")
    s = Search(index="scientific_articles").query(multi_match_query)
    response = s.execute()
    results = [
        {
            "title": hit.title,
            "authors": hit.authors,
            "institutions": hit.institutions,
            "keywords": hit.keywords,
            "pdf_url": hit.pdf_url,
            "bibliographie": hit.bibliographie,
            "text": hit.text,
            "date": hit.date,
        }
        for hit in response
    ]
    return render(request, "search_articles.html", {"query": query, "results": results})

"""
"""def search_articles(request):
    query = request.GET.get("q", "")
    selected_author = request.GET.get("author", "")

    fields = ["title", "authors", "keywords"]
    multi_match_query = MultiMatch(query=query, fields=fields, type="phrase")
    s = Search(index="scientific_articles").query(multi_match_query)
    response = s.execute()

    # Extract unique authors from search results
    authors = list(set([author for hit in response for author in hit.authors]))

    if selected_author:
        s = s.filter("term", authors=selected_author)

    results = [
        {
            "title": hit.title,
            "authors": hit.authors,
            "institutions": hit.institutions,
            "keywords": hit.keywords,
            "pdf_url": hit.pdf_url,
            "bibliographie": hit.bibliographie,
            "text": hit.text,
            "date": hit.date,
            "summary": hit.summary,
        }
        for hit in response
    ]
    for r in results :
        print("resulats:" , r)
        print("\n")
    return render(request, "search_articles.html", {"query": query, "results": results, "authors": authors})
"""
"""def filter_articles_authors(request):
    selected_authors = request.GET.getlist('authors[]')

    # Create a query to filter by selected authors
    s = Search(index="scientific_articles").query("terms", authors=selected_authors)
    response = s.execute()

    filtered_results = [
        {
            "title": hit.title,
            "authors": hit.authors,
            "institutions": hit.institutions,
            "keywords": hit.keywords,
            "pdf_url": hit.pdf_url,
            "bibliographie": hit.bibliographie,
            "text": hit.text,
            "date": hit.date,
        }
        for hit in response
    ]

    return render(request, "filtered_articles.html", {"results": filtered_results})
"""
