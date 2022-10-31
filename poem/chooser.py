import random
import math

from django.db.models import Q, Avg

from .models import Word, Template
from .casetense import NounTransformer, VerbTransformer
from .extract import WordCleaner

class WordChooser():
    def __init__(self):
        self.verb_transformer = VerbTransformer()
        self.noun_transformer = NounTransformer()
        self.cleaner = WordCleaner()
    
    def choose_verb(self, text, voice, singular, verb_tense):
        return self.verb_transformer.conjugate(text, voice, singular, verb_tense)
    
    def choose_noun_or_pronoun(self, text, pos_tag, dependency_label, voice, singular):
        return self.noun_transformer.transform(text, pos_tag, dependency_label, voice, singular)

    def choose(self, pos_tag, dependency_label, ancestor_text, ancestor_pos_tag, ancestor_dependency_label, voice, singular, verb_tense):

        print(pos_tag, dependency_label, ancestor_text, ancestor_pos_tag, ancestor_dependency_label)



        # choose random word. TODO: make swappable random selection model
        # For now, this biases the more common half of available words based on average count

        # ROOT word wordlist (no ancestor)
        if (ancestor_dependency_label=='ZZZ' and ancestor_pos_tag=='ZZZ'):
            wordlist = Word.objects.filter(pos_tag=pos_tag, dependency_label=dependency_label,)
        
        # Assume there is a matching ancestor with the chosen text. If not, do another random lookup without the ancestor.
        else: 
            # prepare ancestor text for db lookup
            ancestor_text = self.cleaner.clean_word(ancestor_text, ancestor_pos_tag, ancestor_dependency_label)

            wordlist = Word.objects.filter(
                pos_tag=pos_tag,
                dependency_label=dependency_label,
                ancestor__pos_tag=ancestor_pos_tag,
                ancestor__dependency_label=ancestor_dependency_label,
                ancestor__text=ancestor_text,
                )
            if not wordlist:
                wordlist = Word.objects.filter(pos_tag=pos_tag, dependency_label=dependency_label,)

        average_count = math.ceil( wordlist.aggregate(Avg('count'))['count__avg'] )
        print('average count: ',average_count)
        wordlist = wordlist.filter(count__gte=average_count)
        max = len(wordlist)
        word = wordlist[ random.randrange(0, max) ]
        
        # conjugate verbs
        if ('VB' in pos_tag) and (dependency_label == 'ROOT' or 'comp' in dependency_label or ('cl' in dependency_label and not 'acl' in dependency_label) or 'conj' in dependency_label):
            text = self.choose_verb(word.text, voice, singular, verb_tense)
        # number nouns/pronouns
        elif 'NN' in pos_tag or 'PRP' in pos_tag or 'WP' in pos_tag:
            text = self.choose_noun_or_pronoun(word.text, pos_tag, dependency_label, voice, singular)
        # handle other parts of speech
        else:
            text = word.text
        
        return text

    def determiner(self, next_word, next_pos_tag, next_dependency_label):
        next_word = next_word.lower()
        next_word = self.cleaner.clean_word(next_word, next_pos_tag, next_dependency_label)
        next_start = next_word[0:2]
        first_letter = next_word[0]

        if next_word in ['house']:
            return 'a'

        if next_start == 'one' or next_start == 'uni' or next_start == 'use':
            return 'a'

        if next_start == 'hou' or next_start == 'hon':
            return 'an'
        
        if first_letter in ['a', 'e', 'i', 'o', 'u']:
            return 'an'
        
        return 'a'

class TemplateChooser():
    def choose(self, num_words, require_root_verb=False, require_root_imperative=False):
        
        # Handle optional Flags
        optional_args = Q()
        if require_root_verb:
            optional_args = optional_args & Q(is_root_verb=True)
        if require_root_imperative:
            options_args = options_args & Q(is_root_imperative=True)
        
        # query DB
        templatelist = Template.objects.filter(optional_args, num_words=num_words)

        # choose random word TODO: make swappable random selection model
        max = len(templatelist)
        return templatelist [ random.randrange(0, max) ]