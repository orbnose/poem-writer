import spacy

nlp = spacy.load('en_core_web_sm')

def bnlp(text):
    return [token.text+'-'+token.dep_+'-'+token.tag_ for token in nlp(text)]