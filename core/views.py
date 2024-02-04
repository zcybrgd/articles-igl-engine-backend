from django.shortcuts import render
from django.utils.datastructures import MultiValueDictKeyError
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.parsers import MultiPartParser
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from django.middleware.csrf import get_token
from Users.models import Moderator, NonUserToken

from .pdf_processing import PDFProcessing

from .pdf_manipulation import PDFManipulation
from .mod_articles import ModArticles
from rest_framework.decorators import authentication_classes, permission_classes


class UploadPDFView(APIView):
    """
        API view for uploading PDF files and extracting data from them.

        This class-based view provides endpoints for uploading PDF files and extracting data from them.

        Methods:
            post: POST request endpoint for uploading PDF files and extracting data.
            get: GET request endpoint to set CSRF token.
    """
    permission_classes = [AllowAny]
    parser_classes = [MultiPartParser]

    @action(detail=False, methods=['post'])
    def post(self, request):
        """
                Upload PDF files and extract data.

                Args:
                    request (HttpRequest): POST request object containing PDF files.

                Returns:
                    Response: HTTP response indicating success or failure of the operation.
        """
        try:
            pdf_url = "NoneAtTheMoment"
            pdf_manipulator = PDFManipulation()
            pdf_files = []
            pdf_processor = PDFProcessing()
            if 'pdf_url' in request.data:
                pdf_url = request.data['pdf_url']
                pdf_file = pdf_manipulator.download_pdf_from_drive(pdf_url)
                pdf_files.append(pdf_file)
            else:
                pdf_files = request.FILES.getlist('pdf_file')
            # extract text from PDF and update the content field
            for pdf_file in pdf_files:
                text, first_page = pdf_manipulator.extract_text_from_pdf(pdf_file)
                #extract each field and form a json of this article
                articleJson = pdf_processor.analyze_extract_data(text, first_page, pdf_url, pdf_file)
                #index this article into es with its status being unreviwed so the moderator would later correct wrong info
                modArt = ModArticles()
                response_of_indexing = modArt.index_article(articleJson)
                print("response of indexing: ", response_of_indexing)
            return Response({'message': 'Files uploaded successfully.'}, status=status.HTTP_201_CREATED)

        except MultiValueDictKeyError:
            return Response({'error': 'PDF file or URL is required.'}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({'error': f'An error occurred: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)



    @action(detail=False, methods=['get'])
    def get(self, request):
        """
                Set CSRF token.

                Args:
                    request (HttpRequest): GET request object.

                Returns:
                    Response: HTTP response indicating success or failure of the operation.
        """
        csrf_token = get_token(request)
        response_data = {'detail': 'CSRF token set successfully', 'X-CSRFToken': csrf_token}
        return Response(response_data)



#this is totally independent
def home(request):
    return render(request, 'home.html')


@authentication_classes([])
@permission_classes([])
class ArticlesApiView(APIView):
    """
        API view for handling articles. All done by the Moderator

        This class-based view provides endpoints for retrieving, deleting, updating, and modifying articles.

        Methods:
            get: GET request endpoint to retrieve unreviewed documents.
            delete: DELETE request endpoint to delete an article.
            post: POST request endpoint to validate an article.
            patch: PATCH request endpoint to modify an article.
    """
    mod_articles = ModArticles()
    @action(detail=False, methods=['get'])
    def get(self, request):
        """
                Retrieve unreviewed documents.

                Args:
                    request (HttpRequest): GET request object.

                Returns:
                    Response: HTTP response containing unreviewed documents.
        """
        documents = self.mod_articles.get_unreviewed_documents()
        return Response({'articles': documents}, status=status.HTTP_200_OK)

    @action(detail=False, methods=['delete'])
    def delete(self, request, article_id):
        """
                Delete an article.

                Args:
                    request (HttpRequest): DELETE request object.
                    article_id (int): ID of the article to be deleted.

                Returns:
                    Response: HTTP response indicating success or failure of the operation.
        """
        key = request.headers['Authorization']
        try:
            token = NonUserToken.objects.get(key=key)
        except NonUserToken.DoesNotExist:
            return Response({'error': "User non authenticated"})
        connected = token.user
        print(connected)
        if connected.id == None:
            return Response({'error': "User non authenticated bel id"})
        if connected.role == "Moderator":
            try:
                mod_connect = Moderator.objects.get(userId=connected)
            except Moderator.DoesNotExist:
                return Response({'error': "the mod user doesn't exist "})
            self.mod_articles.delete_from_elastic_search(article_id)
            mod_connect.delete_count = mod_connect.delete_count + 1  # to increment the delete_count of the mod connected
            mod_connect.save()
            return Response({'message': 'Article deleted successfully'}, status=status.HTTP_200_OK)
        else:
            return Response({'error': "the user is not a moderator "})

    @action(detail=False, methods=['post'])
    def post(self, request):
        """
                Validate an article.

                Args:
                    request (HttpRequest): POST request object.

                Returns:
                    Response: HTTP response indicating success or failure of the operation.
        """
        key = request.headers['Authorization']
        try:
            token = NonUserToken.objects.get(key=key)
        except NonUserToken.DoesNotExist:
            return Response({'error': "User non authenticated"})
        connected = token.user
        print(connected)
        if connected.id == None:
            return Response({'error': "User non authenticated"})
        if connected.role == "Moderator":
            try:
                mod_connect = Moderator.objects.get(userId=connected)
            except Moderator.DoesNotExist:
                return Response({'error': "the mod user doesn't exist "})
            try:
                article_id = request.data.get('id')
                if article_id is None:
                    raise ValueError("'id' field is required.")
                response = self.mod_articles.update_to_elastic_search(article_id)
                if response['success']:
                    mod_connect.validate_count = mod_connect.validate_count+1   # to increment the validated_count of the mod connected
                    mod_connect.save()
                    return Response({'message': 'Article validate successfully'}, status=status.HTTP_200_OK)
                else:
                    return Response({'message': 'Failed to validate article'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            except Exception as e:
                return Response({'message': 'Exception Failed to validate article'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        else:
            return Response({'error': "the user is not a moderator "})

    @action(detail=False, methods=['patch'])
    def patch(self, request, article_id):
        """
                Modify an article.

                Args:
                    request (HttpRequest): PATCH request object.
                    article_id (int): ID of the article to be modified.

                Returns:
                    Response: HTTP response indicating success or failure of the operation.
        """
        key = request.headers['Authorization']
        try:
            token = NonUserToken.objects.get(key=key)
        except NonUserToken.DoesNotExist:
            return Response({'error': "User non authenticated"})
        connected = token.user
        print(connected)
        if connected.id == None:
            return Response({'error': "User non authenticated"})
        if connected.role == "Moderator":
            try:
                mod_connect = Moderator.objects.get(userId=connected)
            except Moderator.DoesNotExist:
                return Response({'error': "the mod user doesn't exist "})
            article_data = request.data
            response = self.mod_articles.modify_elastic_search(article_id, article_data)
            if response['success']:
                mod_connect.edit_count = mod_connect.edit_count+1   # to increment the edit_count of the mod connected
                mod_connect.save()
                return Response({'message': 'Article modified successfully'}, status=status.HTTP_200_OK)
            else:
                return Response({'message': 'Failed to modify article'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        else:
            return Response({'error': "the user is not a moderator "})
