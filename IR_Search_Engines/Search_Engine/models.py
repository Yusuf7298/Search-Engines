from django.db import models

class Document(models.Model):
    title = models.CharField(max_length=200)
    content = models.TextField()
    class Meta:
        indexes = [
            models.Index(fields=['content'], name='content_idx'),
        ]
    def __str__(self):
        return self.title

class DocumentChunk(models.Model):
    document = models.ForeignKey(Document, on_delete=models.CASCADE, related_name='chunks')
    content = models.TextField()
    page_number = models.IntegerField(default=0)
    class Meta:
        indexes = [
            models.Index(fields=['content'], name='chunk_content_idx'),
        ]