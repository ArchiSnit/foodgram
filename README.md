# 🍽️ Foodgram — Социальная платформа для любителей готовить и делиться рецептами

[![Русский](https://img.shields.io/badge/Language-Русский-blue)](README.md)
[![English](https://img.shields.io/badge/Language-English-blue)](README_EN.md)

Foodgram — это соцсеть, где пользователи могут делиться рецептами, искать вдохновение и создавать списки покупок. Платформа предназначена для кулинарных энтузиастов, которые любят делиться идеями и находить новые блюда.

## ✨ Основные возможности
- 📝 **Публикация рецептов**: добавляйте блюда с фото, описанием и инструкциями по приготовлению.
- ❤️ **Избранное**: сохраняйте понравившиеся рецепты для быстрого доступа.
- 🔔 **Подписки**: следите за любимыми авторами и их новыми публикациями.
- 🛒 **Список покупок**: формируйте и скачивайте список ингредиентов для выбранных блюд.
- 🔍 **Поиск и фильтрация**: находите рецепты по тегам и времени приёма пищи.

## 🛠 Технологический стек

| Технология                      | Описание                              |
|----------------------------------|---------------------------------------|
| Django                           | Фреймворк для бэкенда                |
| Django REST Framework            | API для взаимодействия с данными      |
| PostgreSQL                       | Реляционная база данных               |
| Docker                           | Контейнеризация и оркестрация        |
| Gunicorn                         | WSGI сервер                           |
| NGINX                            | Прокси-сервер                        |

## 🚀 Запуск проекта локально

Чтобы запустить проект на вашем компьютере, выполните следующие шаги:

1. Клонируйте репозиторий:
bash

   git clone git@github.com:ArchiSnit/foodgram.git


   cd foodgram 


   

markdown

 Копировать код
2. Создайте и настройте `.env`:
   Скопируйте `.env.example`, переименуйте в `.env` и заполните.

   **Пример**:

   SECRET_KEY='django-insecure-!65y-r4+hsr!9xgb+d5=r+!!wk3(8^x58i#f)y_&=owq9q!b08'


   DEBUG=True


   ALLOWED_HOSTS='food-graminia.hopto.org,127.0.0.1,localhost,84.201.142.83'


   POSTGRES_USER=foodgram_user


   POSTGRES_PASSWORD=foodgram_password


   DB_NAME=foodgram


   POSTGRES_DB=foodgram


   DJANGO_SUPERUSER_EMAIL=4yva4ok8@gmail.com


   DJANGO_SUPERUSER_USERNAME=Admin


   DJANGO_SUPERUSER_FIRST_NAME=Arsen


   DJANGO_SUPERUSER_SECOND_NAME=K


   DJANGO_SUPERUSER_PASSWORD=4815162342Admin1


   

markdown

 Копировать код
3. Запустите Docker:
bash

   docker-compose up -d --build  


   

markdown

 Копировать код
4. Доступ к проекту:
   Откройте [http://localhost:8080](http://localhost:8080) или [http://food-graminia.hopto.org](http://food-graminia.hopto.org) в браузере.

## 🔧 Полезные команды

| Команда                                    | Назначение                              |
|--------------------------------------------|-----------------------------------------|
| `docker ps -a`                             | Просмотр запущенных контейнеров        |
| `docker-compose down -v`                   | Остановка и удаление контейнеров и томов|
| `docker image rm $(docker image ls -q)`   | Удаление всех образов проекта           |

## 👨‍💻 Автор
- Бэкенд: Арсен Карапетян
- Фронтенд: Команда Яндекс Практикума

🎉 **Присоединяйтесь к Foodgram!**   
Делитесь своими кулинарными идеями и вдохновляйтесь рецептами других! 🍲✨



