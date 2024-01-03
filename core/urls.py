from django.urls import path
from .views import home, UploadPDFView, ArticlesApiView



urlpatterns = [
    path('api/uploadPDF', UploadPDFView.as_view(), name='uploadPDF'),
    path('', home, name='home'),
    path('api/articles/', ArticlesApiView.as_view(), name='articles-api'),
    path('api/articles/<str:article_id>', ArticlesApiView.as_view(), name='delete-article'),
    path('api/articles/<str:article_id>/update/', ArticlesApiView.as_view(), name='update-article'),
]

#urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
