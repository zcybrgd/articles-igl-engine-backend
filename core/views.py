import os
import requests
from django.core.files.uploadedfile import InMemoryUploadedFile
from django.shortcuts import render
from django.utils.datastructures import MultiValueDictKeyError
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.parsers import FileUploadParser, MultiPartParser, FormParser
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView
from .models import Article
from django.middleware.csrf import get_token
from .serializers import ArticleSerializer

class UploadPDFView(APIView):
    serializer_class = ArticleSerializer
    queryset = Article.objects.all()
    parser_classes = [FileUploadParser]
    permission_classes = [AllowAny]
    parser_classes = [MultiPartParser]

    @action(detail=False, methods=['post'])
    def post(self, request):
        try:
            pdf_url = "NoneAtTheMoment"

            if 'pdf_url' in request.data:
                pdf_url = request.data['pdf_url']
                pdf_file = self.download_pdf_from_drive(pdf_url)
            else:
                pdf_file = request.FILES['pdf_file']

            # Extract text from PDF and update the content field
            text = self.extract_text_from_pdf(pdf_file)
            print("textyy: ", text)
            article = Article.objects.create(
                content=text,
                url_pdf=pdf_url,
            )
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

    def get_drive_direct_link(self, gdrive_link):
        # Extract the file ID from the shareable link
        file_id = gdrive_link.split("/")[-2]
        # Construct the direct download link
        direct_download_link = f'https://drive.google.com/u/0/uc?id={file_id}&export=download'

        return direct_download_link



    def download_pdf_from_drive(self, pdf_url):
        from io import BytesIO
        # Get the direct download link
        direct_link = self.get_drive_direct_link(pdf_url)
        # Download the PDF from the direct link
        response = requests.get(direct_link)

        # Check if the download was successful (status code 200)
        if response.status_code == 200:
            pdf_content = response.content
            pdf_file = InMemoryUploadedFile(
                file=BytesIO(pdf_content),
                field_name=None,
                name='downloaded.pdf',
                content_type='application/pdf',
                size=len(pdf_content),
                charset=None
            )
            print("PDF downloaded successfully.")
            return pdf_file  # Return the downloaded PDF file
        else:
            # Handle the case where the request to the URL was not successful
            print(f"Failed to download PDF from URL. Status code: {response.status_code}")
            return None

    @action(detail=False, methods=['get'])
    def get(self, request):
        csrf_token = get_token(request)
        response_data = {'detail': 'CSRF token set successfully', 'X-CSRFToken': csrf_token}

        return Response(response_data)


    def extract_text_from_pdf(self, pdf_file):
        import fitz
        import tempfile
        # Save the InMemoryUploadedFile to a temporary file
        with tempfile.NamedTemporaryFile(delete=False) as temp_file:
                for chunk in pdf_file.chunks():
                    temp_file.write(chunk)

        # Open the temporary file with PyMuPDF
        doc = fitz.open(temp_file.name)
        text = ''
        for page_num in range(doc.page_count):
                page = doc[page_num]
                text += page.get_text()

        # Close the PyMuPDF document
        doc.close()

        # Clean up: delete the temporary file
        os.unlink(temp_file.name)

        return text

def home(request):
    return render(request, 'home.html')