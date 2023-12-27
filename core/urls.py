from django.urls import path
from .views import home, UploadPDFView, ArticlesApiView # Import the home view



urlpatterns = [
    path('api/uploadPDF', UploadPDFView.as_view(), name='uploadPDF'),
    path('', home, name='home'),
    path('api/articles/', ArticlesApiView.as_view(), name='articles-api'),
    path('api/articles/<int:article_id>', ArticlesApiView.as_view(), name='delete-article'),
]

#urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)