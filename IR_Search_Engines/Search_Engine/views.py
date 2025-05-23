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
            total_docs = documents.count()

            # Build index and compute TF-IDF
            inverted_index, document_lengths, unique_terms = search_utils.build_inverted_index(documents)
            tfidf_index, tf_values, idf_values = search_utils.calculate_tfidf(inverted_index, total_docs)
            raw_results = search_utils.search(query, tfidf_index, document_lengths)
            probabilities = search_utils.compute_probabilities(query, tfidf_index, document_lengths)

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

            context = {
                'results': results,
                'query': query,
                'count': len(results),
                'index_terms_count': len(unique_terms),
                'document_lengths': document_lengths,
                'tf_values': tf_values,
                'idf_values': idf_values,
                'tfidf_index': tfidf_index,
                'probabilities': probabilities,
            }

            if not results:
                context['error'] = 'No results found'

            paginator = Paginator(results, 10)
            page_number = request.GET.get('page', 1)
            context['page_obj'] = paginator.get_page(page_number)

            return render(request, 'Search_Engine/results.html', context)

        except Exception as e:
            logger.error(f"Search error: {str(e)}")
            return render(request, 'Search_Engine/search.html', {
                'error': 'An error occurred during search'
            })

    return render(request, 'Search_Engine/search.html')
