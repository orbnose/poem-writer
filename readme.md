1. Create venv and install dependencies
```
pip install spacy, nltk, inflect, mlconjug3
```
2. Download required nltk components.
```
python
import nltk
nltk.download('wordnet')
nltk.download('omw-1.4')
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
