FOR LOCAL USE 

REQUREMENT: 
    virtual environment
    django installed. 
        If not: run this command in the virtual environment: pip install django

HOW TO RUN: 
    In your shell type: 
        python manage.py makemigrations
        python manage.py migrate
        python manage.py runserver
    In your browser: 
        127.0.0.1:8000

Note: You can only register a psychologist by web interface if you are superuser. 
Tests are in users/tests.py folder.