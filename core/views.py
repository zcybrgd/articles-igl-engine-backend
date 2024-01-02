from django.shortcuts import render
from django.utils.datastructures import MultiValueDictKeyError
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.parsers import MultiPartParser
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView
from .models import Article
from django.middleware.csrf import get_token

from .pdf_processing import PDFProcessing
from .serializers import ArticleSerializer, ArticleUnReviewedSerializer
from .pdf_manipulation import PDFManipulation
from .mod_articles import ModArticles
from rest_framework.decorators import authentication_classes, permission_classes


class UploadPDFView(APIView):
    serializer_class = ArticleSerializer
    queryset = Article.objects.all()
    permission_classes = [AllowAny]
    parser_classes = [MultiPartParser]

    @action(detail=False, methods=['post'])
    def post(self, request):
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
            return Response({'message': 'Files uploaded successfully.'}, status=status.HTTP_201_CREATED)

        except MultiValueDictKeyError:
            return Response({'error': 'PDF file or URL is required.'}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({'error': f'An error occurred: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)



    @action(detail=False, methods=['get'])
    def get(self, request):
        csrf_token = get_token(request)
        response_data = {'detail': 'CSRF token set successfully', 'X-CSRFToken': csrf_token}
        return Response(response_data)




def home(request):
    return render(request, 'home.html')


@authentication_classes([])
@permission_classes([])
class ArticlesApiView(APIView):
    mod_articles = ModArticles()
    @action(detail=False, methods=['get'])
    def get(self, request):
        documents = self.mod_articles.get_unreviewed_documents()
        return Response({'articles': documents}, status=status.HTTP_200_OK)

    @action(detail=False, methods=['delete'])
    def delete(self, request, article_id):
        self.mod_articles.delete_from_elastic_search(article_id)
        return Response({'message': 'Article deleted successfully'}, status=status.HTTP_200_OK)

    @action(detail=False, methods=['post'])
    def post(self, request):
        try:
            article_id = request.data.get('id')
            if article_id is None:
                raise ValueError("'id' field is required.")
            response = self.mod_articles.update_to_elastic_search(article_id)
            if response['success']:
                return Response({'message': 'Article validate successfully'}, status=status.HTTP_200_OK)
            else:
                return Response({'message': 'Failed to validate article'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        except Exception as e:
            return Response({'message': 'Failed to validate article'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    @action(detail=False, methods=['patch'])
    def patch(self, request, article_id):
        article_data = request.data
        response = self.mod_articles.modify_elastic_search(article_id, article_data)
        if response['success']:
            return Response({'message': 'Article modified successfully'}, status=status.HTTP_200_OK)
        else:
            return Response({'message': 'Failed to modify article'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
