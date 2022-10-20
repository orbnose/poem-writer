import inflect
from nltk.stem.wordnet import WordNetLemmatizer

class NounTransformer():
# Transformations on a noun based on requested case.
#  Assumes english part of speech tagging provided by spacy - see https://v2.spacy.io/api/annotation#pos-tagging

    def __init__(self):
        self.inflector = inflect.engine()
        
        # pronoun_dict['pronoun'] = ['singular form', 'plural form']
        self.pronoun_dict = {
                'all': ['one','all'],
                'another': ['another','others'],
                'anybody': ['anybody','all'],
                'anyone': ['anyone','all'],
                'anything': ['anything','all things'],
                'both': ['either','both'],
                'each': ['each','all'],
                'either': ['either','both'],
                'enough': ['enough','enough things'],
                'everybody': ['everybody','all'],
                'everyone': ['everyone','all'],
                'everything': ['everything','all things'],
                'few': ['one', 'few'],
                'he': ['he','they'],
                'her': ['her','their'],
                'hers': ['hers','theirs'],
                'herself': ['herself','themselves'],
                'him': ['him','them'],
                'himself': ['himself','themselves'],
                'his': ['his','theirs'],
                'I': ['I','we'],
                'it': ['it','they'],
                'its': ['its','their'],
                'itself': ['itself','theirselves'],
                'many': ['one','many'],
                'me': ['me','us'],
                'mine': ['mine','ours'],
                'most': ['one','most'],
                'my': ['my','our'],
                'myself': ['myself','ourselves'],
                'neither': ['neither','none'],
                'nobody': ['nobody','none'],
                'none': ['neither','none'],
                'nothing': ['nothing','none'],
                'one': ['one','many'],
                'other': ['other','others'],
                'others': ['other','others'],
                'our': ['my','our'],
                'ours': ['mine','ours'],
                'ourself': ['myself','ourself'],
                'ourselves': ['myself','ourselves'],
                'several': ['one','several'],
                'she': ['she','they'],
                'some': ['one','some'],
                'somebody': ['somebody','all'],
                'someone': ['someone','all'],
                'something': ['something','all things'],
                'such': ['such','such things'],
                'that': ['that','these'],
                'thee': ['thee','ye'],
                'their': ['her','their'],
                'theirs': ['hers','theirs'],
                'theirself': ['herself','theirself'],
                'theirselves': ['herself','theirselves'],
                'them': ['her','them'],
                'themself': ['herself','themself'],
                'themselves': ['herself','themselves'],
                'these': ['this','these'],
                'they': ['she','they'],
                'thine': ['thine','thine'],
                'this': ['this','these'],
                'those': ['that','those'],
                'thou': ['thou','ye'],
                'thy': ['thy','your'],
                'thyself': ['thyself','yourselves'],
                'us': ['me','us'],
                'we': ['I','we'],
                'what': ['what','what things'],
                'whatever': ['whatever','whatever things'],
                'which': ['which','which'],
                'whichever': ['whichever','whichever'],
                'whichsoever': ['whichsoever','whichsoever'],
                'who': ['who','who all'],
                'whoever': ['whoever','who all'],
                'whom': ['whom','whom'],
                'whomever': ['whomever','whomever'],
                'whomso': ['whomso','whomso'],
                'whomsoever': ['whomsoever','whomsoever'],
                'whose': ['whose','whose'],
                'whosever': ['whosever','whosever'],
                'whosesoever': ['whosesoever','whosesoever'],
                'whoso': ['whoso','who all'],
                'whosoever': ['whosoever','whosoever all'],
                'ye': ['thee','ye'],
                'you': ['you','you'],
                'your': ['your','your'],
                'yours': ['your','your'],
                'yourself': ['yourself','yourselves'],
                'yourselves': ['yourself','yourselves'],
        }

    def transform_pronoun(self, text, singular=True):
        
        # setup dictionary controls
        if singular:
            lookup = 0
        else:
            lookup = 1
        
        if text in self.pronoun_dict:
            return self.pronoun_dict[text][lookup]
        else:
            return None

    def transform(self, text, pos_tag, singular=True):
        
        # Convert the text to lowercase if not a proper noun
        if not (pos_tag == 'NNP' or pos_tag == 'NNPS'):
            text = text.lower()
        
        # Handle pronouns
        if (pos_tag == 'PRP' or pos_tag == 'WP'):
            pronoun = self.transform_pronoun(text, singular=singular)
            if pronoun:
                return pronoun
            return text
        
        # Handle non-pronouns
        if singular:
            noun = self.inflector.singular_noun(text)
        else:
            noun = self.inflector.plural_noun(text)
        if noun:
            return noun
        return text

class VerbTransformer():
    pass

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