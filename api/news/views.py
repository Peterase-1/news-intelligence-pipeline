
import sys
import os
import logging
from rest_framework import viewsets
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

# Add project root to path for Imports
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

# Import Pipeline Components
try:
    from nlp.embeddings.generator import EmbeddingGenerator
    from vector_store.chroma.client import NewsVectorStore
    AI_AVAILABLE = True
except ImportError:
    AI_AVAILABLE = False
    print("⚠️ AI Components not found. RAG will be disabled.")

from .models import NewsArticle
from .serializers import NewsArticleSerializer

logger = logging.getLogger(__name__)

# 1. Standard News API
class NewsArticleViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API endpoint that allows news to be viewed.
    Supports filtering by source, sentiment, etc.
    """
    queryset = NewsArticle.objects.all().order_by('-published_at')
    serializer_class = NewsArticleSerializer
    filterset_fields = ['source', 'sentiment_label']
    search_fields = ['title', 'body_text']

# 2. RAG Chat API
class RAGChatView(APIView):
    """
    Endpoint for Intelligence Search.
    POST {"query": "Tell me about..."}
    """
    def post(self, request):
        if not AI_AVAILABLE:
            return Response({"error": "AI Engine unavailable"}, status=503)

        query_text = request.data.get("query")
        if not query_text:
            return Response({"error": "Query is required"}, status=400)

        try:
            # A. Embed Query
            generator = EmbeddingGenerator() # Can be optimized to load once
            query_vector = generator.generate(query_text)

            # B. Search Vector DB
            vector_store = NewsVectorStore()
            results = vector_store.search(query_vector, n_results=3)
            
            # C. Format Response
            docs = []
            if results and results['documents']:
                for i in range(len(results['documents'][0])):
                    docs.append({
                        "id": results['ids'][0][i],
                        "text": results['documents'][0][i],
                        "metadata": results['metadatas'][0][i]
                    })
            
            return Response({
                "query": query_text,
                "answer": "Here are the most relevant news articles:",
                "results": docs
            })

        except Exception as e:
            logger.error(f"RAG Error: {e}")
            return Response({"error": str(e)}, status=500)
