В процессе заполнения 


Находясь в папке infra, выполните команду docker-compose up. При выполнении этой команды контейнер frontend, описанный в docker-compose.yml, подготовит файлы, необходимые для работы фронтенд-приложения, а затем прекратит свою работу.

По адресу http://localhost изучите фронтенд веб-приложения, а по адресу http://localhost/api/docs/ — спецификацию API.

Авторство
Фронтенд — команда Яндекс Практикума.
Бэкенд — Карапетян Арсен






python manage.py createsuperuser

django-admin startproject backend  

python manage.py startapp api



Cоздание админа в контейнере 
docker exec -it foodgram-back bash


Загрузка в БД
python manage.py import_ingredients


source venv/Scripts/activate


pip install -r requirements.txt

pip install --upgrade pip

python manage.py makemigrations

python manage.py migrate

python manage.py runserver






docker compose exec backend python manage.py migrate

docker compose exec backend python manage.py collectstatic

docker compose exec backend cp -r /app/collected_static/. /backend_static/static/





