# Streamada-Backend: Django Project

## Project Overview
This is a Django project that uses Redis for caching and All-Inkl web services for email services. To ensure that the project runs correctly, developers must rename the `.env.example` file to `.env` and insert their respective credentials and required configuration values.


## Requirements
Ensure that the following dependencies are installed on your system:
- Recommended: Linux-Ubuntu (or another Linux distribution)
- PostgreSQL oder SQLite (depending on database configuration)
- Frontend project (required for full functionality)
- Frontend:``` git clone https://github.com/Hamzaba92/streamada_frontend.git ```

## Local Setup

### 1. Clone repository
Clone the repository into your local directory:
```bash
git clone https://github.com/Hamzaba92/streamada_backend.git
```

### 2. Change .env.example to .env
```bash
.env.example =change to => .env
```

### 3. Create a virtual environment and activate it
```bash 
# Windows
python -m venv env
env\Scripts\activate

# Linux
python3 -m venv env
source env/bin/activate
```

### 5. Install all requirements listed in requirements.txt
```bash
pip install -r requirements.txt
```

### 6. Create a database
```bash 
linux: 1. => python3 manage.py makemigrations 2. => python3 manage.py migrate
windwos: 1. => python manage.py makemigrations 2. => python manage.py migrate
```

### 7. Create a superuser to access the admin panel
```bash
linux: python3 manage.py createsuperuser
windows: python manage.py createsuperuser
```

### 8. Start the server
```bash
linux: python3 manage.py runserver
windows: python manage.py runserver
```


## Functionality of the Web-App
Ensure that the frontend is already running.

### Registration & Activation Link
```bash
the activation link will appear in your terminal, Please activate your account trough the terminal.
```

### After Succesfully Login
You can upload a video trough the Admin Panel.
Make sure Redis and rqworker are running.
To test if Redis is working, open redis CLI and write a ping. If the response is "Pong", Redis working: 
```bash
redis-cli  
```

### Open a New Terminal and Activate the rqworker
```bash
python3 manage.py rqworker
```

### Video Conversion Process
Once the worker is active, it will convert the uploaded video into 480p, 720p, and 1080p versions.
```bash
You will then be able to see the video in your frontend application.
```