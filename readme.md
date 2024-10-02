# Streamada-Backend: Django Project

## Project Overview
This is a Django project that uses Redis for caching and All-Inkl web services for email services. To ensure that the project runs correctly, developers must rename the `.env.example` file to `.env` and insert their respective credentials and required configuration values.


## Requirements
Ensure that the following dependencies are installed on your system:
- Python 3.x
- Pipenv oder venv (Virtuelle Umgebung)
- Redis (optional, for Caching)
- PostgreSQL oder SQLite (depending on database configuration)
- Das frontend project (required for full functionality)
- Frontend:``` git clone https://github.com/Hamzaba92/streamada_frontend.git ```

## Local Setup

### 1. Repository klonen
Clone the repository into your local directory:
```bash
git clone https://github.com/Hamzaba92/streamada_backend.git
```
### 2. Navigate to the folder
```bash
cd streamada_backend
```
### 3. Change .env.example to .env
```bash
.env.example =change to=> .env
```
### 4. Create a virtual environment and activate it
```bash 
Windowns: python -m venv env => env/Scripts/activate
Linux: python3 -m venv env => source env/bin/activate
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
### 8. Starte the server
```bash
linux: python3 manage.py runserver
windows: python manage.py runserver
```

