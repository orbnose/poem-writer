1. Create venv and install spacy
```
pip install spacy
```

2. download the English language model
```
python -m spacy download en_core_web_sm
```

3. Run Django migrations
```
python manage.py makemigrations db
python manage.py migrate
```

4. Run test.py