"""from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from .models import Document,DocumentChunk
from .tasks import rebuild_inverted_index_background_task

@receiver(post_save, sender=Document)
@receiver(post_delete, sender=Document)
@receiver(post_save, sender=DocumentChunk)
@receiver(post_delete, sender=DocumentChunk)
def document_changed(sender, instance, **kwargs):
    print("Rebuilding TFIDF matrix due to object changes")
    rebuild_inverted_index_background_task.delay()"""


from django.dispatch import receiver
from django.db.models.signals import post_save
from .models import Document,DocumentChunk

def register_signals():
    from .tasks import rebuild_inverted_index_background_task
    
    @receiver(post_save, sender=Document)
    def trigger_rebuild(sender, instance, **kwargs):
        rebuild_inverted_index_background_task.delay()