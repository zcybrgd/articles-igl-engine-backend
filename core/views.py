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
            pdf_processor = PDFProcessing()
            cleaner = TextCleaner()
            if 'pdf_url' in request.data:
                pdf_url = request.data['pdf_url']
                pdf_file = pdf_manipulator.download_pdf_from_drive(pdf_url)
            else:
                pdf_file = request.FILES['pdf_file']
            # Extract text from PDF and update the content field
            text, first_page = pdf_manipulator.extract_text_from_pdf(pdf_file)
            article = Article.objects.create(
                content=text,
                url_pdf=pdf_url,
            )
            # extract abstract, and then references, and then keywords, and then clean the text
            # and then authors and organizations
            abstract, text_without_abstract = pdf_processor.extract_abstract(text)
            references, text_without_references = pdf_processor.extract_references(text_without_abstract)
            keywords = pdf_processor.extract_keywords(text_without_references)
            objectAuthorOrg = pdf_processor.spacyNER(first_page)
            print("\nFirst page:\n", first_page)
            print("\nAbstract:\n",abstract)
            print("\nReferences:\n",references)
            print("\nKeywords:\n", keywords)
            print("\n\nAuteurs et org\n", objectAuthorOrg)
            print("\n\n\ntitle: \n", pdf_processor.detect_article_title(first_page))
            #textFINAL = cleaner.cleaning_text(text_without_references)
            #print("\n\n\nRest of text:\n", textFINAL)'''
            article.save()
            serializer = ArticleSerializer(article, data=request.data)
            if serializer.is_valid():
                serializer.save()
                return Response({'message': 'File uploaded successfully.'}, status=status.HTTP_201_CREATED)
            else:
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        except MultiValueDictKeyError:
            return Response({'error': 'PDF file or URL is required.'})
        except Exception as e:
            return Response({'error': f'An error occurred: {str(e)}'})



    @action(detail=False, methods=['get'])
    def get(self, request):
        csrf_token = get_token(request)
        response_data = {'detail': 'CSRF token set successfully', 'X-CSRFToken': csrf_token}
        return Response(response_data)




def home(request):
    return render(request, 'home.html')