from django import forms
from .models import UploadedDocument

# class ImageUploadForm(forms.ModelForm):
#     class Meta:
#         model = UploadedImage
#         fields = ('image',)


class DocumentUploadForm(forms.ModelForm):
    class Meta:
        model = UploadedDocument
        fields = ['file', 'date', 'subject', 'sender', 'recipient', 'cc', 'keywords']