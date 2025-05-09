from django.shortcuts import render
from django.core.paginator import Paginator
from . import search_utils
from .models import Document
import logging

logger = logging.getLogger(__name__)

def search_view(request):
    if request.method == 'POST':
        query = request.POST.get('search_query', '').strip()
        
        if not query:
            return render(request, 'Search_Engine/search.html', {
                'error': 'Please enter a search term'
            })
        
        try:
            documents = Document.objects.all()
            inverted_index = search_utils.build_inverted_index(documents)
            total_docs = documents.count()
            tfidf_index = search_utils.calculate_tfidf(inverted_index, total_docs)
            raw_results = search_utils.search(query, tfidf_index, documents)
            
            results = []
            for doc_id, score in raw_results:
                try:
                    doc = documents.get(id=doc_id)
                    results.append({
                        'title': doc.title,
                        'content': doc.content[:200] + '...' if len(doc.content) > 200 else doc.content,
                        'score': round(score, 4)
                    })
                except Document.DoesNotExist:
                    continue
            
            logger.debug(f"Found {len(results)} results for query: {query}")
            
            if not results:
                return render(request, 'Search_Engine/search.html', {
                    'error': 'No results found',
                    'query': query
                })
            
            paginator = Paginator(results, 10)
            page_number = request.GET.get('page', 1)
            page_obj = paginator.get_page(page_number)
            
            return render(request, 'Search_Engine/results.html', {
                'results': page_obj,
                'query': query,
                'count': len(results)
            })
            
        except Exception as e:
            logger.error(f"Search error: {str(e)}")
            return render(request, 'Search_Engine/search.html', {
                'error': 'An error occurred during search'
            })
    
    return render(request, 'Search_Engine/search.html')