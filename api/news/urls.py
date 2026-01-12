
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import NewsArticleViewSet, RAGChatView

router = DefaultRouter()
router.register(r'news', NewsArticleViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('chat/', RAGChatView.as_view(), name='rag-chat'),
]
