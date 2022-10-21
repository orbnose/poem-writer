import inflect
import mlconjug3
from nltk.stem.wordnet import WordNetLemmatizer

from .pronoun import Pronoun, validate_voice, validate_singular

def convert_label_and_tag(spacy_dep_label, pos_tag):
    if (
        '$' in pos_tag or 
        'POS' in pos_tag
    ):
        return 'poss'
    elif (
        'obj' in spacy_dep_label or 
        'dative' in spacy_dep_label or
        'comp' in spacy_dep_label
    ):
        return 'obj'

    # fallback default
    return 'subj'

class NounTransformer():
# Transformations on a noun based on requested case.
#  Assumes english part of speech tagging and 
#  dependency labels provided by spacy - see https://v2.spacy.io/api/annotation#pos-tagging

    def __init__(self):
        self.inflector = inflect.engine()
        self.pronoun_transformer = Pronoun()

    def transform(self, text, pos_tag, dependency_label, voice='third', singular=True, force_pronoun_selection=True):
        
        # Handle pronouns
        if ('PRP' in pos_tag or 'WP' in pos_tag):
            # convert spacy dep label to pronoun transformer label
            transform_label = convert_label_and_tag(dependency_label, pos_tag)

            # get pronoun
            return self.pronoun_transformer.transform(
                text,
                voice=voice,
                dependency_label=transform_label,
                singular=singular,
                force_selection=force_pronoun_selection 
            )
        
        # Handle non-pronouns
        if singular:
            noun = self.inflector.singular_noun(text)
        else:
            noun = self.inflector.plural_noun(text)
        if noun:
            return noun
        return text

    def transform_for_db(self, text, pos_tag, dependency_label, voice='third', singular=True):
        
        # Convert the text to lowercase if not a proper noun
        if not (pos_tag == 'NNP' or pos_tag == 'NNPS'):
            text = text.lower()

        return self.transform(
            text=text,
            pos_tag=pos_tag,
            dependency_label=dependency_label, 
            voice=voice,
            singular=singular, 
            force_pronoun_selection=False # Don't restrict words getting into the db in case my dictionary is incomplete
        )

class VerbTransformer():

    def __init__(self):
        self.lemmatizer = WordNetLemmatizer()
        self.conjugator = mlconjug3.Conjugator(language='en')

        self.voice_choices = {
            "first": '1',
            "second": '2',
            "third": '3',
        }

        self.singular_choices = {
            True: 's',
            False: 'p',
        }
        self.tense_options = (
            'indicative present', 'indicative past tense', 'indicative present continuous', 'indicative present perfect',
            'infinite present',
            'imperative present',
        )
        # mlconjug3 conjug_info OrderedDict categories:
            # indicative
                # indicative present
                # indicative past tense
                # indicative present continuous
                # indicative present perfect        
            # infinitive
                # infinitive present         
            # imperative
                # imperative present

    def translate_verb_case(self, voice, singular):
        return self.voice_choices[voice] + self.singular_choices[singular]

    def transform_for_db(self, text):

        text = text.lower()
        singular_verb = self.lemmatizer.lemmatize(text,'v')
        if singular_verb:
            return singular_verb
        return text
    
    def conjugate(self, text, voice, singular, verb_tense):
        
        # validate verb_tense
        if not verb_tense in self.tense_options:
            raise ValueError('invalid tense option')
        # validate voice
        validate_voice(voice)
        # validate singular
        validate_singular(singular)

        # split verb_tense string by the first space, and this will be the mlconjug3 verb category. (See layout under self.tense_options.)
        verb_category = verb_tense.split()[0]

        # translate verb case
        verb_case = self.translate_verb_case(voice, singular)

        return self.conjugator.conjugate(text).conjug_info[verb_category][verb_tense][verb_case]


    