import os
import fitz
import tempfile
import requests
from django.core.files.uploadedfile import InMemoryUploadedFile
from io import BytesIO

from core.pdf_title import pdf_title


class PDFManipulation():
    """
       Class for manipulating PDF files.

       This class provides methods for extracting text from PDF files, downloading PDF files from Google Drive,
       and extracting the title from the content of a PDF file.

       this is what happens first when the Adminstrator uploads a bunch of pdf articles
       Attributes:
           None
       """
    def extract_text_from_pdf(self, pdf_file):
        """
                Extract text from a PDF file.

                Args:
                    pdf_file: An uploaded PDF file.

                Returns:
                    tuple: A tuple containing the extracted text and the text from the first page of the PDF.
        """
        # Save the InMemoryUploadedFile to a temporary file that we gonna get rid off it after extracting the text
        with tempfile.NamedTemporaryFile(delete=False) as temp_file:
            for chunk in pdf_file.chunks():
                temp_file.write(chunk)
        doc = fitz.open(temp_file.name)
        text = ''
        first_page = ''
        for page_num in range(doc.page_count):
            page = doc[page_num]
            text += page.get_text()
            if page_num==0:
                first_page = text

        doc.close()
        os.unlink(temp_file.name)
        return text, first_page

    def get_drive_direct_link(self, gdrive_link):
        """
                Get the direct download link from a Google Drive shareable link.

                Args:
                    gdrive_link (str): The Google Drive shareable link.

                Returns:
                    str: The direct download link for the PDF file.
        """
        file_id = gdrive_link.split("/")[-2]
        direct_download_link = f'https://drive.google.com/u/0/uc?id={file_id}&export=download'
        return direct_download_link

    def download_pdf_from_drive(self, pdf_url):
        """
               Download a PDF file from a Google Drive link.

               Args:
                   pdf_url (str): The URL of the PDF file hosted on Google Drive.

               Returns:
                   InMemoryUploadedFile: The downloaded PDF file as an in-memory uploaded file object.
        """
        direct_link = self.get_drive_direct_link(pdf_url)
        response = requests.get(direct_link)
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
            return pdf_file
        else:
            print(f"Failed to download PDF from URL. Status code: {response.status_code}")
            return None

    def pdf_title_from_content(self, pdf_file):
        """
                Extract the title from the content of a PDF file.

                Args:
                    pdf_file: An uploaded PDF file.

                Returns:
                    str: The title extracted from the PDF content.
        """
        with tempfile.NamedTemporaryFile(delete=False) as temp_pdf:
            for chunk in pdf_file.chunks():
                temp_pdf.write(chunk)

        temp_pdf_path = temp_pdf.name
        title = pdf_title(temp_pdf_path)
        temp_pdf.close()
        os.unlink(temp_pdf.name)
        return title