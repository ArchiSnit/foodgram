🍽️ Foodgram — A Social Platform for Cooking Enthusiasts
Foodgram is a community where users can share recipes,
find inspiration, and create shopping lists.
It is designed for food lovers who enjoy sharing ideas and discovering new dishes.

✨ Key Features
📝 Recipe Publishing: Upload your dishes with photos, descriptions, and step-by-step instructions.
❤️ Favorites: Save your favorite recipes for quick access.
🔔 Subscriptions: Follow your favorite authors and keep up with their latest recipes.
🛒 Shopping List: Generate and download ingredient lists for selected recipes.
🔍 Search and Filtering: Find recipes by tags and meal times.
🛠 Technology Stack
Technology	Description
Django	Backend framework
Django REST Framework	API for data interaction
PostgreSQL	Relational database
Docker	Containerization and orchestration
Gunicorn	WSGI server
NGINX	Proxy server

🚀 How to Run Locally
Follow these steps to run the project on your local machine:

1️⃣ Clone the Repository:


git clone git@github.com:ArchiSnit/foodgram.git 
cd foodgram2️⃣ Create and Configure .env:
   Copy .env.example, rename it to .env, and fill in the details.   Example:
   SECRET_KEY='your-secret-key'
   DEBUG=True
   ALLOWED_HOSTS='your-domain.com,127.0.0.1,localhost'
   POSTGRES_USER=your_username
   POSTGRES_PASSWORD=your_password
   DB_NAME=your_db_name
   POSTGRES_DB=your_postgres_db_name
   DJANGO_SUPERUSER_EMAIL=your_email@example.com
   DJANGO_SUPERUSER_USERNAME=your_username
   DJANGO_SUPERUSER_FIRST_NAME=YourFirstName
   DJANGO_SUPERUSER_SECOND_NAME=YourLastName
   DJANGO_SUPERUSER_PASSWORD=your_superuser_password3️⃣
3️⃣ Run Docker:


docker-compose up -d --build  
4️⃣ Access the Application:
Open http://localhost:8080 or http://food-graminia.hopto.org in your browser.

🔧 Useful Commands
Command	Purpose
docker ps -a	List running containers
docker-compose down -v	Stop and remove containers and volumes
docker image rm $(docker image ls -q)	Remove all project images
👨‍💻 Author
Backend: Arsen Karapetyan
Frontend: Yandex Practicum Team
🎉 Join Foodgram!
Share your culinary ideas and get inspired by others! 🍲✨