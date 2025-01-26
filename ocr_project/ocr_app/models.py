from django.db import models

# class UploadedImage(models.Model):
#     image = models.ImageField(upload_to='uploads/')
#     uploaded_at = models.DateTimeField(auto_now_add=True)

class UploadedDocument(models.Model):
    file = models.FileField(upload_to='uploads/')
    date = models.CharField(max_length=255, null=True, blank=True)
    subject = models.CharField(max_length=255, null=True, blank=True)
    sender = models.CharField(max_length=255, null=True, blank=True)
    recipient = models.CharField(max_length=255, null=True, blank=True)
    cc = models.TextField(null=True, blank=True)
    keywords = models.TextField(null=True, blank=True)

    def __str__(self):
        return f"Document {self.id}"

