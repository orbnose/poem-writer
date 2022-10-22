import random

from .models import Word
from .casetense import NounTransformer, VerbTransformer

class WordChooser():
    def __init__(self):
        self.verb_transformer = VerbTransformer()
        self.noun_transformer = NounTransformer()
    
    def choose_verb(self, text, voice, singular, verb_tense):
        return self.verb_transformer.conjugate(text, voice, singular, verb_tense)
    
    def choose_noun_or_pronoun(self, text, pos_tag, dependency_label, voice, singular):
        return self.noun_transformer.transform(text, pos_tag, dependency_label, voice, singular)

    def choose(self, pos_tag, dependency_label, voice, singular, verb_tense):
        
        # handle punctuation
        if dependency_label == 'punct':
            return '.'

        # choose random word. TODO: make swappable random selection model
        wordlist = Word.objects.filter(pos_tag=pos_tag, dependency_label=dependency_label)
        max = len(wordlist)
        word = wordlist[ random.randrange(0, max) ]
        
        # conjugate verbs
        if dependency_label == 'ROOT':
            text = self.choose_verb(word.text, voice, singular, verb_tense)
        # number nouns/pronouns
        elif 'NN' in pos_tag or 'PRP' in pos_tag or 'WP' in pos_tag:
            text = self.choose_noun_or_pronoun(word.text, pos_tag, dependency_label, voice, singular)
        # handle other parts of speech
        else:
            text = word.text
        
        return text
            