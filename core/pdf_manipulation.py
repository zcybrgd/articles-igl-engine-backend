import os
import fitz
import tempfile
import requests
from django.core.files.uploadedfile import InMemoryUploadedFile
from io import BytesIO
class PDFManipulation():
    def extract_text_from_pdf(self, pdf_file):
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
            if page_num==0:
                first_page = text

        # Close the PyMuPDF document
        doc.close()
        # Clean up: delete the temporary file
        os.unlink(temp_file.name)
        return text, first_page


    def get_drive_direct_link(self, gdrive_link):
        # Extract the file ID from the shareable link
        file_id = gdrive_link.split("/")[-2]
        # Construct the direct download link
        direct_download_link = f'https://drive.google.com/u/0/uc?id={file_id}&export=download'

        return direct_download_link

    def download_pdf_from_drive(self, pdf_url):
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

