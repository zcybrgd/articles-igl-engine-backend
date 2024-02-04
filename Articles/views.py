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
    """
        API view to handle manipulation of favorite articles for clients.

        This class-based view provides endpoints for displaying, adding, and removing favorite articles for client users.

        Methods:
            display_favorite_articles: GET request endpoint to display favorite articles for the authenticated client user.
            add_to_favorite: POST request endpoint to add an article to the authenticated client user's favorites.
            remove_favorite: DELETE request endpoint to remove an article from the authenticated client user's favorites.
    """
    @api_view(['GET'])
    def display_favorite_articles(request):
        """
                Display favorite articles for the authenticated client user.

                Args:
                    request (HttpRequest): GET request object.

                Returns:
                    JsonResponse: JSON response containing the favorite articles.
        """
        connected = request.user
        if connected.id == None:
            return Response({'error': 'User non authenticated'})

        if connected.role == "Client":
            try:
                clientConnected = client.objects.get(userId=connected)
            except client.DoesNotExist:
                return Response({'error': "the client user doesn't exist "})
            favorite_article_ids = clientConnected.favorite_articles
            s = Search(index='article_index').filter('ids', values=favorite_article_ids)
            response = s.execute()
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

            return JsonResponse({'favorite_articles': results})
        else:
            return Response({'error': 'Action accessible only for Client users'})

    @api_view(['POST'])
    def add_to_favorite(request, article_id):
        """
                Add an article to the authenticated client user's favorites.

                Args:
                    request (HttpRequest): POST request object.
                    article_id (int): ID of the article to be added to favorites.

                Returns:
                    JsonResponse: JSON response indicating success or failure of the operation.
        """
        connected = request.user
        if connected.id == None:
            return Response({'error': 'User non authenticated'})
        if connected.role == "Client":
            try:
                clientConnected = client.objects.get(userId=connected)
            except client.DoesNotExist:
                return Response({'error': "the client user doesn't exist "})

            if article_id not in clientConnected.favorite_articles:
                clientConnected.favorite_articles.append(article_id)
                clientConnected.save()
            else:
                return Response({'error': 'Article already added to favorites'})
            serializer = ClientSerializer(clientConnected)

            return JsonResponse({'success': True, 'message': 'Article added to favorites', 'user': serializer.data})
        else:
            return Response({'error': 'Action accessible only for Client users'})

    @api_view(['DELETE'])
    def remove_favorite(request, article_id):
        """
                Remove an article from the authenticated client user's favorites.

                Args:
                    request (HttpRequest): DELETE request object.
                    article_id (int): ID of the article to be removed from favorites.

                Returns:
                    JsonResponse: JSON response indicating success or failure of the operation.
        """
        connected = request.user
        if connected.id == None:
            return Response({'error': 'User non authenticated'})
        if connected.role == "Client":
            try:
                clientConnected = client.objects.get(userId=connected)
            except client.DoesNotExist:
                return Response({'error': "the client user doesn't exist "})

            if article_id in clientConnected.favorite_articles:
                clientConnected.favorite_articles.remove(article_id)
                clientConnected.save()
            else:
                return Response({'error': 'Article doesn''t figure in your favorite list'})

            serializer = ClientSerializer(clientConnected)

            return JsonResponse({'success': True, 'message': 'Article removed successfully', 'user': serializer.data})
        else:
            return Response({'error': 'Action accessible only for Client users'})
