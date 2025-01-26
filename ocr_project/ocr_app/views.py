import os
from django.contrib import messages
import re
from django.shortcuts import redirect, render
from django.core.files.storage import FileSystemStorage
from django.conf import settings

from ocr_app.models import UploadedDocument
from .forms import DocumentUploadForm
from collections import Counter
from pytesseract import image_to_string, pytesseract
from PIL import Image

# Set the Tesseract executable path if it's not in your PATH
pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"



def extract_metadata(text, lang):
    if lang == 'amh':
        # Amharic Metadata Extraction
        date = re.search(r"(Date|ቀን)[^\n:]*[:\-]?\s*(.*)", text)
        subject = re.search(r"ጉዳዩ[:\-]?\s*(.*)", text)
        sender = re.search(r"ከ[:\-]?\s*(.+?)\s*(ለ|$)", text)
        recipient = re.search(r"ለ[:\-]?\s*(.*)", text)
        cc = re.search(r"ግልባጭ[:\-]?\s*(.*)", text)

    elif lang == 'eng':
        # English Metadata Extraction
        date = re.search(r"Date[:\-]?\s*(\d{4}-\d{2}-\d{2})", text)
        subject = re.search(r"Subject[:\-]?\s*(.+)", text)
        sender = re.search(r"Yours sincerely,\s*(.+)", text)
        recipient = re.search(r"To[:\-]?\s*(.+)", text)
        cc = re.search(r"(CC|Carbon Copy)[:\-]?\s*(.+)", text)


    else:
        return {}

    # Tokenize and filter out stopwords
    words = re.findall(r'\b\w+\b', text)  # Extract words only (alphanumeric)
    if lang == 'amh':
        relevant_words = [word for word in words if all('ሀ' <= char <= 'ፚ' for char in word)]  # Amharic range
    else:
        relevant_words = [word.lower() for word in words if word.isalnum()]  # English

    keywords = Counter(relevant_words).most_common(10)

    return {
        "date": date.group(1) if date else None,
        "subject": subject.group(1).strip() if subject else "",
        "sender": sender.group(1).strip() if sender else "",
        "recipient": recipient.group(1).strip() if recipient else "",
        "cc": cc.group(1).strip() if cc else "",
        "keywords": ", ".join(word for word, _ in keywords)
    }


def upload_image(request):
    extracted_text = None
    metadata = {}
    selected_language = None
    languages = {
        'eng': 'English',
        'amh': 'Amharic',
    }
    
    if request.method == 'POST':
        form = DocumentUploadForm(request.POST, request.FILES)
        selected_language = request.POST.get('language', 'eng')  # Default to English
        print(f"Selected Language: {selected_language}")  # Debugging

        if form.is_valid():
            try:
                document = form.save(commit=False)
                print("Form is valid, saving file...")  # Debugging

                # Save the uploaded file
                upload_dir = os.path.join(settings.MEDIA_ROOT, 'uploads')
                fs = FileSystemStorage(location=upload_dir)
                filename = fs.save(document.file.name, document.file)
                file_path = fs.path(filename)
                print(f"File saved at: {file_path}")  # Debugging

                # Perform OCR
                extracted_text = image_to_string(Image.open(file_path), lang=selected_language)
                print(f"Extracted Text: {extracted_text[:100]}")  # Debugging (first 100 chars)

                # Extract metadata
                metadata = extract_metadata(extracted_text, selected_language)
                print(f"Extracted Metadata: {metadata}")  # Debugging
                amharic_date_pattern = r'[\u1200-\u137F]+ \d{1,2} \d{4}'
                matches = re.findall(amharic_date_pattern, extracted_text)
                print(matches)
                # Pre-fill the form with metadata
                form = DocumentUploadForm(initial={
                    "file": document.file,
                    "date": metadata.get('date'),
                    "subject": metadata.get('subject'),
                    "sender": metadata.get('sender'),
                    "recipient": metadata.get('recipient'),
                    "cc": metadata.get('cc'),
                    "keywords": metadata.get('keywords'),
                })
                document.save()

                return render(request, 'ocr_app/display_form.html', {
                    'form_data': metadata,
                    'form': form,
                    'file_id': document.id,
                })
            except Exception as e:
                print(f"Error: {str(e)}")  # Debugging
                metadata = {"error": f"An error occurred: {str(e)}"}

    else:
        form = DocumentUploadForm()

    return render(request, 'ocr_app/upload.html', {
        'form': form,
        'extracted_text': extracted_text,
        'languages': languages,
        'selected_language': selected_language,
    })


def save_metadata(request, file_id):
    document = UploadedDocument.objects.get(id=file_id)
    print(f"Document: {document}")  # Debugging

    if request.method == 'POST':
        form = DocumentUploadForm(request.POST, instance=document)
        if form.is_valid():
            form.save()
            messages.success(request, 'Document metadata saved successfully.')
            return redirect('upload_image')
        else:
            messages.error(request, 'There was an error saving the document metadata.')
    else:
        form = DocumentUploadForm(instance=document)

    return render(request, 'ocr_app/display_form.html', {
        'form_data': document,
        'form': form,
        'file_id': document.id,
    })



