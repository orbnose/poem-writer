import spacy
import random
from .chooser import WordChooser
from .models import Word

def get_cased_noun(text, singular, inflector):
    if singular:
        cased_noun = inflector.singular_noun(text)
    else:
        cased_noun = inflector.plural_noun(text)
    
    if cased_noun:
        return cased_noun
    return text

def make_line():

    # control panel
    template_text = "I eat dirt. I digest. My body learns to protect against the swallowed microbes. I paradoxically improve by eating harmful biota."
        #template_text = "Dogs dig holes, and cats sleep in the shade."
    singular = True
    voice = 'second'
    verb_tense = 'indicative present'
    
    # prepare data/tools
    nlp = spacy.load('en_core_web_sm')
    chooser = WordChooser()
    template_doc = nlp(template_text)
    template = []
    sentence = []

    if singular:
        verb_case = '3s'
    else:
        verb_case = '3p'

    # build template
    for token in template_doc:
        label = str(token.dep_)
        if label == "ROOT":
            label = 'root verb'
        pos_tag = token.tag_
        template.append( [label, pos_tag] )
    
    # choose words
    for word_template in template:
        label = word_template[0]
        pos_tag = word_template[1]
        text = chooser.choose(pos_tag, label, voice, singular, verb_tense)
        sentence.append(text)
    
    # print sentence

    sentence_text = ""
    for text in sentence:
        if text == '.':
            sentence_text = sentence_text[:-1] #remove last space
        sentence_text = sentence_text + text + " "
    print('\n', sentence_text, '\n')
    print(str(template))
