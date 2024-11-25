






























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


python manage.py show_urls


docker compose exec backend python manage.py migrate

docker compose exec backend python manage.py collectstatic

docker compose exec backend cp -r /app/collected_static/. /backend_static/static/


cd frontend  # В директории frontend...
docker build -t arsen551/foodgram_frontend . 

cd ../backend  # То же в директории backend...
docker build -t arsen551/foodgram_backend .

cd ../gateway  # ...то же и в gateway
docker build -t arsen551/foodgram_gateway . 

docker-compose up --build -d

docker push arsen551/foodgram_backend
docker push arsen551/foodgram_frontend
docker push arsen551/foodgram_gateway

