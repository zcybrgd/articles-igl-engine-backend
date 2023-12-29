# search/views.py
import json

from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import render, get_object_or_404
from elasticsearch_dsl import Search
from elasticsearch_dsl.query import Terms, Match
from rest_framework.response import Response
from rest_framework.decorators import permission_classes, api_view, authentication_classes
from rest_framework import permissions

from Users.models import client
from Users.serializers import ClientSerializer
from search.search_indexes import ArticleIndex

@authentication_classes([])
@permission_classes([])
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

        return JsonResponse({'favorite_articles': response.to_dict()})
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

            # Check if the article_id is not already in the favorite_articles array
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