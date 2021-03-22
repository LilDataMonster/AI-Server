from django.urls import path
from rest_framework.urlpatterns import format_suffix_patterns
from api import views


urlpatterns = [
    path('yolov5/image', views.YoloV5UploadImageView.as_view()),
    path('yolov5/metadata', views.YoloV5UploadMetadataView.as_view()),
    path('tesseract/image', views.TesseractUploadImageView.as_view()),
    path('tesseract/metadata', views.TesseractUploadMetadataView.as_view()),
    # path('snippets/<int:pk>/', views.SnippetDetail.as_view()),
]

urlpatterns = format_suffix_patterns(urlpatterns)