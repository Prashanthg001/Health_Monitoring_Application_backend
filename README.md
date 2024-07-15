1. Clone the repo
2. Get into the folder
3. Create python environment
    python -m venv myenv
4. activate environment
    .\myenv\Scripts\activate
5. install requirements
    pip install -r requirements.txt
    (or)
    pip install django
    pip install spacy
    python -m spacy download en_core_web_sm
    pip install djangorestframework
    pip install djangorestframework djangorestframework-simplejwt
6. Make migrations and migrate
    python manage.py makemigrations
    python manage.py migrate
    python manage.py runserver
7. admin login
    username: Testing02
    password: Test@1234