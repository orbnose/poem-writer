from db.config import configureDjango
import spacy
import random
import mlconjug3
from casetense import NounTransformer

def get_cased_noun(text, singular, inflector):
    if singular:
        cased_noun = inflector.singular_noun(text)
    else:
        cased_noun = inflector.plural_noun(text)
    
    if cased_noun:
        return cased_noun
    return text

def main():
    from db.models import Word
    
    # control panel
    template_text = "I eat dirt. I digest. My body learns to protect against the swallowed microbes. I paradoxically improve by eating harmful biota."
    #template_text = "Dogs dig holes, and cats sleep in the shade."
    singular = True # False for plural
    verb_category = 'indicative'
    verb_tense = 'indicative present'
    
    # prepare data/tools
    nlp = spacy.load('en_core_web_sm')
    conjugator = mlconjug3.Conjugator(language='en')
    noun_transformer = NounTransformer()
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
    
    # look up words
    for word_template in template:
        label = word_template[0]
        pos_tag = word_template[1]

        if label == 'punct':
            sentence.append('.')
        else:
            wordlist = Word.objects.filter(pos_tag=pos_tag, dependency_label=label)
            max = len(wordlist)
            word = wordlist[ random.randrange(0, max) ]
            
            # conjugate verbs
            if label == 'root verb':
                text = conjugator.conjugate(word.text).conjug_info[verb_category][verb_tense][verb_case]
            # number nouns
            elif 'nsub' in label or 'nn' in label or 'obj' in label or 'noun' in label:
                text = noun_transformer.transform(word.text, pos_tag, singular=singular)
            # handle other parts of speech
            else:
                text = word.text
            sentence.append(text)
    
    # print sentence

    sentence_text = ""
    for text in sentence:
        if text == '.':
            sentence_text = sentence_text[:-1] #remove last space
        sentence_text = sentence_text + text + " "
    print('\n', sentence_text, '\n')
    print(str(template))

if __name__ == "__main__":
	configureDjango()
	main()
