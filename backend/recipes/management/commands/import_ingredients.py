# Вариант загрузки в БД в формате csv
import csv
import os
from django.core.management.base import BaseCommand
from recipes.models import Ingredient, Tag


class Command(BaseCommand):
    help = 'Импортирует ингредиенты из файла CSV'

    def handle(self, *args, **kwargs):
        """
        Обрабатывает команду для импорта ингредиентов из файла CSV.

        Читает данные из CSV файла и добавляет их в базу данных.
        Если ингредиент с таким же именем уже существует, он игнорируется.
        Для каждого добавленного
        Или существующего ингредиента выводится сообщение.
        """

        # Определяет путь к CSV файлу
        path_to_file = os.path.join(
            os.path.dirname(__file__), '..', '..', 'data', 'ingredients.csv')

        # Открывает CSV файл для чтения
        with open(path_to_file, newline='', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                # Получает или создает ингредиент на основе данных из CSV
                ingredient, created = Ingredient.objects.get_or_create(
                    name=row['name'],
                    measurement_unit=row['measurement_unit']
                )

                if created:
                    # Вывод сообщения об успешном добавлении нового ингредиента
                    self.stdout.write(self.style.SUCCESS(
                        f'Ингредиент добавлен: {ingredient}'))
                else:
                    # Вывод предупреждения об уже существующем ингредиенте
                    self.stdout.write(self.style.WARNING(
                        f'Ингредиент уже существует: {ingredient}'))

        # Импорт тегов
        tags = [
            ('завтрак', 'breakfast'),
            ('обед', 'lunch'),
            ('ужин', 'dinner'),
        ]
        self.stdout.write('Начинаю загрузку тегов в базу...')

        # Создание объектов тегов
        tag_objects = [Tag(name=name, slug=slug) for name, slug in tags]
        Tag.objects.bulk_create(tag_objects, ignore_conflicts=True)

        self.stdout.write(
            f'Загрузка в базу - ЗАВЕРШЕНА\n'
            f'Всего тегов в базе: {Tag.objects.count()}\n'
            f'-----------------------------------------------'
        )
