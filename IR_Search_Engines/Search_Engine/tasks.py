from celery import shared_task
from . import search_utils
from django.core.cache import cache

@shared_task
def rebuild_inverted_index_background_task():
    print("Start indexing")
    inverted_index = search_utils.build_inverted_index_background()
    cache.set("inverted_index", inverted_index, 300)
    return "Indexing Complete!"