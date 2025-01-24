# from django.shortcuts import render
# from .forms import ImageUploadForm
# from pytesseract import image_to_string, pytesseract
# from PIL import Image
# import os

# # Set the Tesseract executable path if it's not in your PATH
# pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

# def upload_image(request):
#     extracted_text = None
#     if request.method == 'POST':
#         form = ImageUploadForm(request.POST, request.FILES)
#         if form.is_valid():
#             image_instance = form.save()
#             image_path = image_instance.image.path

#             # Perform OCR using Tesseract
#             extracted_text = image_to_string(Image.open(image_path), lang='amh')
#     else:
#         form = ImageUploadForm()
#     return render(request, 'ocr_app/upload.html', {'form': form, 'extracted_text': extracted_text})
import re
from django.shortcuts import render
from .forms import ImageUploadForm
from pytesseract import image_to_string, pytesseract
from PIL import Image

# Set the Tesseract executable path if it's not in your PATH
pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

# Regex for detecting words after "ከ" and "ለ"
from_to_regex = r'ከ\s+(.+?)\s+ለ\s+(.+)'


def upload_image(request):
    extracted_text = None
    selected_language = None
    languages = {
        'eng': 'English',
        'amh': 'Amharic',
        'osd': 'Orientation Script Detection',
        'Ethiopic': 'Ethiopic Script',
    }

    from_name = None  # Initialize from_name
    to_name = None    # Initialize to_name

    if request.method == 'POST':
        form = ImageUploadForm(request.POST, request.FILES)
        selected_language = request.POST.get('language', 'eng')  # Default to English

        if form.is_valid():
            image_instance = form.save()
            image_path = image_instance.image.path

            # Perform OCR using the selected language
            extracted_text = image_to_string(Image.open(image_path), lang=selected_language)

            # Search for the words after "ከ" and "ለ" in the extracted text using regex
            match = re.search(from_to_regex, extracted_text)

            if match:
                from_name = match.group(1)  # Name after "ከ"
                to_name = match.group(2)    # Name after "ለ"

    else:
        form = ImageUploadForm()

    return render(request, 'ocr_app/upload.html', {
        'form': form,
        'extracted_text': extracted_text,
        'languages': languages,
        'selected_language': selected_language,
        'from_name': from_name,
        'to_name': to_name,
    })



# const similarWordsRegex = /መጽሓፍ/g;  // For exact match

#  Or, if you want to find partial matches (e.g., if a user writes "መጽሓፍ" as "መጽሓፍስ"):
# const flexibleWordRegex = /መጽሓፍ[^ ]*/g;