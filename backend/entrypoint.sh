 #!/bin/bash

# Запуск миграций
echo "Выполняю миграции..."
python manage.py makemigrations
python manage.py migrate --noinput

# Копирование медиа и статики
echo "Копирование медиа и статических файлов..."
cp -r /app/media/. /media/
python manage.py collectstatic --no-input
echo "Статические файлы собраны."
cp -r /app/collected_static/. /backend_static/static/
echo "Собранные статические файлы скопированы."
cp -r /app/docs/. /docs/
echo "Документация скопирована."


# Импорт ингредиентов
echo "Импортируем ингредиенты..."
python manage.py import_ingredients
echo "Ингредиенты успешно импортированы."

# Создание суперпользователя
echo "Создаю суперпользователя..."
if ! python -c "from django.contrib.auth import get_user_model; User = get_user_model(); User.objects.get(username='$DJANGO_SUPERUSER_USERNAME')" 2>/dev/null; then
    python manage.py createsuperuser --noinput --username "$DJANGO_SUPERUSER_USERNAME" --email "$DJANGO_SUPERUSER_EMAIL" --first_name "$DJANGO_SUPERUSER_FIRST_NAME" --last_name "$DJANGO_SUPERUSER_SECOND_NAME"
    python -c "from django.contrib.auth import get_user_model; User = get_user_model(); user = User.objects.get(username='$DJANGO_SUPERUSER_USERNAME'); user.set_password('$DJANGO_SUPERUSER_PASSWORD'); user.save();"
else
    echo "Суперпользователь уже существует."
fi


# Запуск Gunicorn
echo "Запускаю Gunicorn..."
gunicorn foodgram_backend.wsgi:application --bind 0.0.0.0:8080
echo "Gunicorn запущен, приятного пользования"
echo "Приложение доступно по адресу https://food-graminia.hopto.org."