# Вариант загрузки в БД в формате json

# import json
# import os
# from django.core.management.base import BaseCommand
# from recipes.models import Ingredient
#
# class Command(BaseCommand):
#     help = 'Импортирует ингредиенты из файла JSON'
#
#     def handle(self, *args, **kwargs):
#         path_to_file = os.path.join(
#             os.path.dirname(__file__), '..', '..', 'data',
#                                           'ingredients.json')
#
#         with open(path_to_file, 'r', encoding='utf-8') as jsonfile:
#             data = json.load(jsonfile)
#             for item in data:
#                 ingredient, created = Ingredient.objects.get_or_create(
#                     name=item['name'],
#                     measurement_unit=item['measurement_unit']
#                 )
#
#                 if created:
#                     self.stdout.write(self.style.SUCCESS(
#                         f'Ингредиент добавлен: {ingredient}'))
#                 else:
#                     self.stdout.write(self.style.WARNING(
#                         f'Ингредиент уже существует: {ingredient}'))
#
