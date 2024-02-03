# search/views.py
from django.http import JsonResponse
from elasticsearch_dsl import Search, AttrList
from rest_framework.response import Response
from rest_framework.decorators import permission_classes, api_view, authentication_classes
from rest_framework.views import APIView

from Users.models import client
from Users.serializers import ClientSerializer


@authentication_classes([])
@permission_classes([])
class FavoritesManipulation(APIView):
    @api_view(['GET'])
    def display_favorite_articles(request):
        connected = request.user
        if connected.id == None:
            return Response({'error': 'User non authenticated'})

        if connected.role == "Client":
            try:
                clientConnected = client.objects.get(userId=connected)
            except client.DoesNotExist:
                return Response({'error': "the client user doesn't exist "})

            # Hardcoded list of favorite article IDs (replace with your actual IDs)
            favorite_article_ids = clientConnected.favorite_articles

            # Build Elasticsearch search query to retrieve favorite articles
            s = Search(index='article_index').filter('ids', values=favorite_article_ids)
            # Execute the search
            response = s.execute()
            # Convert Elasticsearch results to a list of dictionaries
            results = [{
                        'id': hit.meta.id,
                        'title': hit.title,
                        'authors': list(hit.authors) if isinstance(hit.authors, AttrList) else hit.authors,
                        'institutions': list(hit.institutions) if isinstance(hit.institutions, AttrList) else hit.institutions,
                        'keywords': hit.keywords,
                        'pdf_url': hit.pdf_url,
                        'bibliographie': list(hit.bibliographie) if isinstance(hit.bibliographie, AttrList) else hit.bibliographie,
                        'abstract': hit.abstract,
                        'text': hit.text,
                        'date': hit.date} for hit in response]

            # Return JSON response
            return JsonResponse({'favorite_articles': results})
        else:
            return Response({'error': 'Action accessible only for Client users'})

    @api_view(['POST'])
    def add_to_favorite(request, article_id):
        connected = request.user
        if connected.id == None:
            return Response({'error': 'User non authenticated'})
        if connected.role == "Client":
            try:
                clientConnected = client.objects.get(userId=connected)
            except client.DoesNotExist:
                return Response({'error': "the client user doesn't exist "})

            # Check if the article_id is not already in the favorite_articles array
            if article_id not in clientConnected.favorite_articles:
                # Add the article_id to the favorite_articles array
                clientConnected.favorite_articles.append(article_id)
                # Save the updated client instance
                clientConnected.save()
            else:
                return Response({'error': 'Article already added to favorites'})
            # Serialize the updated client instance
            serializer = ClientSerializer(clientConnected)

            return JsonResponse({'success': True, 'message': 'Article added to favorites', 'user': serializer.data})
        else:
            return Response({'error': 'Action accessible only for Client users'})

    @api_view(['DELETE'])
    def remove_favorite(request, article_id):
        connected = request.user
        if connected.id == None:
            return Response({'error': 'User non authenticated'})
        if connected.role == "Client":
            try:
                clientConnected = client.objects.get(userId=connected)
            except client.DoesNotExist:
                return Response({'error': "the client user doesn't exist "})

            # Check if the article_id is in the favorite_articles array
            if article_id in clientConnected.favorite_articles:
                # Remove the article_id from the favorite_articles array
                clientConnected.favorite_articles.remove(article_id)

                # Save the updated client instance
                clientConnected.save()
            else:
                return Response({'error': 'Article doesn''t figure in your favorite list'})

            # Serialize the updated client instance
            serializer = ClientSerializer(clientConnected)

            return JsonResponse({'success': True, 'message': 'Article removed successfully', 'user': serializer.data})
        else:
            return Response({'error': 'Action accessible only for Client users'})
