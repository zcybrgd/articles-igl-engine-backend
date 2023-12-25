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
from .serializers import ArticleSerializer
from .pdf_manipulation import PDFManipulation
from.pdf_processing import PDFProcessing
from .pdf_cleaning import TextCleaner
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

            if 'pdf_url' in request.data:
                pdf_url = request.data['pdf_url']
                pdf_file = pdf_manipulator.download_pdf_from_drive(pdf_url)
                pdf_files.append(pdf_file)
            else:
                pdf_files = request.FILES.getlist('pdf_file')

            # Extract text from PDF and update the content field
            for pdf_file in pdf_files:
                text, first_page = pdf_manipulator.extract_text_from_pdf(pdf_file)
                article_data = {
                    'content': text,
                    'url_pdf': pdf_url,
                }
                print("\n\nfirst page: \n", first_page)
                serializer = ArticleSerializer(data=article_data)
                if serializer.is_valid():
                    serializer.save()
                else:
                    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

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