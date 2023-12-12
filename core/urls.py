from django.urls import path
from .views import home, UploadPDFView  # Import the home view



urlpatterns = [
    path('api/uploadPDF', UploadPDFView.as_view(), name='uploadPDF'),
    path('', home, name='home'),
]

#urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)