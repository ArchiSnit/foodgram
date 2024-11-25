import os
import base64

from io import BytesIO
from datetime import datetime
from django.conf import settings
from reportlab.pdfgen import canvas
from django.http import HttpResponse
from rest_framework import serializers
from reportlab.lib.pagesizes import A4
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from django.core.files.base import ContentFile


# Путь к шрифту
ROBOTO_FONT_PATH = os.path.join(
    settings.BASE_DIR, 'fonts', 'roboto', 'Roboto-Bold.ttf')

# Константа для директории shop_list
SHOP_LIST_DIR = os.path.join(
    settings.BASE_DIR, 'recipes', 'data', 'shop_list')


def create_shopping_list_pdf(ingredients):
    """
    Создаёт PDF-документ со списком покупок
    с использованием шрифта Roboto.
    """
    os.makedirs(SHOP_LIST_DIR, exist_ok=True)
    filename = f"shopping_list_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
    file_path = os.path.join(SHOP_LIST_DIR, filename)

    pdf_buffer = BytesIO()
    document = canvas.Canvas(pdf_buffer, pagesize=A4)

    # Регистрация шрифта Roboto
    pdfmetrics.registerFont(TTFont('Roboto', ROBOTO_FONT_PATH))
    document.setFont('Roboto', 16)

    # Заголовок
    document_title = "Список покупок"
    page_width, page_height = A4
    title_width = document.stringWidth(document_title, 'Roboto', 16)
    title_x = (page_width - title_width) / 2
    document.drawString(title_x, page_height - 50, document_title)

    # Список ингредиентов
    document.setFont('Roboto', 12)
    text_y = page_height - 100
    item_number = 1

    for item in ingredients:
        name = item['recipe__ingredients__name']
        quantity = item['total_amount']
        unit = item['recipe__ingredients__measurement_unit']
        line_text = f"{item_number}. {name}: {quantity} {unit}"
        document.drawString(80, text_y, line_text)
        item_number += 1
        text_y -= 20

        if text_y < 50:
            document.showPage()
            document.setFont('Roboto', 12)
            text_y = page_height - 50

    document.save()
    pdf_buffer.seek(0)

    with open(file_path, 'wb') as pdf_file:
        pdf_file.write(pdf_buffer.getvalue())

    response = HttpResponse(pdf_buffer, content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="{filename}"'

    return response


class Base64ImageField(serializers.ImageField):
    """Для расшифровки изображений (аватар и рецепт)."""
    def to_internal_value(self, data):
        if isinstance(data, str) and data.startswith('data:image'):
            format, imgstr = data.split(';base64,')
            ext = format.split('/')[-1]
            data = ContentFile(base64.b64decode(imgstr), name='temp.' + ext)
        return super().to_internal_value(data)
